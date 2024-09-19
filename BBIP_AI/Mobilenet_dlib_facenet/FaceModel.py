import os
import cv2
import dlib
import numpy as np
import torch
import torch.nn as nn
from deepface import DeepFace
import tensorflow.lite as tflite

class CombinedFaceModel(nn.Module):
    def __init__(self):
        super(CombinedFaceModel, self).__init__()
        self.landmark_detector = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

        # TFLite 모델 초기화
        self.interpreter = tflite.Interpreter("ssd_mobilenet_v2_face_quant_postprocess.tflite")
        self.interpreter.allocate_tensors()

    def forward(self, img):
        # img가 PyTorch 텐서인 경우 NumPy 배열로 변환
        if isinstance(img, torch.Tensor):
            numpy_img = img.permute(0, 2, 3, 1).detach().numpy()  # (N, C, H, W) -> (N, H, W, C)
            if numpy_img.ndim == 4:  # 배치 차원 제거
                numpy_img = numpy_img[0]  # 첫 번째 배치만 사용

        # 얼굴 검출
        faces = self.face_detection(numpy_img)
        embeddings = []

        for face in faces:
            # 얼굴 정렬
            routesCrd, landmarksTuples, face_img = self.faceAlignment(numpy_img, face)
            # 얼굴 회전
            rotated_face_img = self.faceRotation(routesCrd, landmarksTuples, face_img)
            # DeepFace로 얼굴 표현 생성
            embedding = self.faceRepresentation(rotated_face_img)
            embeddings.append(embedding)
        # 임베딩이 없을 경우 빈 텐서 반환
        if not embeddings:
            return torch.empty(0)  # 빈 텐서 반환    
        return torch.stack(embeddings)  # 리스트를 텐서로 변환
        
    def face_detection(self, img):
        # 이미지가 비어있는지 확인
        if img is None or img.size == 0:
            raise ValueError("Input image is empty or None.")

        # 이미지 속성 확인
        print("Input image shape:", img.shape)  # 이미지의 형태
        print("Input image dtype:", img.dtype)  # 데이터 타입
        print("Input image dimensions:", img.ndim)  # 차원 수
        print("Input image size:", img.size)  # 총 요소 수
        print("Input image max value:", np.max(img))  # 최대 값
        print("Input image min value:", np.min(img))  # 최소 값

        # 이미지 원본 크기 저장
        original_height, original_width = img.shape[:2]
        scale_x = original_width / 320
        scale_y = original_height / 320

        # 이미지 리사이즈
        image_resized = cv2.resize(img, dsize=(320, 320), interpolation=cv2.INTER_AREA)

        # 입력 텐서 준비
        tensor = self.input_tensor()

        # 데이터 복사 및 형식 맞춤 (명시적 복사)
        tensor[:] = image_resized.astype(np.float32).copy()  # .copy()를 추가하여 참조 방지

        # 추론 시작
        self.interpreter.invoke()

        # 결과 가져오기
        objs = self.get_output(0.5, (scale_x, scale_y))
        
        return objs  # [x_min, y_min, x_max, y_max] 형식의 리스트


    def input_tensor(self):
        """Returns input tensor view as numpy array."""
        tensor_index = self.interpreter.get_input_details()[0]['index']
        return self.interpreter.tensor(tensor_index)()[0].copy()

    def get_output(self, score_threshold, image_scale):
        """Returns list of detected objects."""
        boxes = self.output_tensor(0)
        class_ids = self.output_tensor(1)
        scores = self.output_tensor(2)
        count = int(self.output_tensor(3))

        width, height = 320, 320  # 리사이즈된 이미지 크기
        image_scale_x, image_scale_y = image_scale
        sx, sy = width / image_scale_x, height / image_scale_y

        def make(i):
            ymin, xmin, ymax, xmax = boxes[i]
            return {
                'id': int(class_ids[i]),
                'score': float(scores[i]),
                'bbox': {
                    'xmin': int(xmin * sx),
                    'ymin': int(ymin * sy),
                    'xmax': int(xmax * sx),
                    'ymax': int(ymax * sy)
                }
            }

        return [make(i) for i in range(count) if scores[i] >= score_threshold]

    def output_tensor(self, i):
        """Returns output tensor view."""
        tensor = self.interpreter.tensor(self.interpreter.get_output_details()[i]['index'])()
        return np.squeeze(tensor)

    def faceAlignment(self, img, face):
        baseImg = img.copy()
        dlib_box = dlib.rectangle(int(face['bbox']['xmin']), int(face['bbox']['ymin']),
                                  int(face['bbox']['xmax']), int(face['bbox']['ymax']))
        landmarks = self.landmark_detector(img, dlib_box)
        landmarksTuples = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(68)]

        routes = [i for i in range(16, -1, -1)] + [i for i in range(17, 27)] + [16]
        routesCrd = []
        for i in range(len(routes) - 1):
            sourceCrd = landmarksTuples[routes[i]]
            targetCrd = landmarksTuples[routes[i + 1]]
            routesCrd.append(sourceCrd)

        routesCrd.append(routesCrd[0])
        mask = np.zeros((img.shape[0], img.shape[1]), dtype=np.uint8)
        mask = cv2.fillConvexPoly(mask, np.array(routesCrd, np.int32), 1)
        out = np.zeros_like(img)
        out[mask == 1] = img[mask == 1]
        return routesCrd, landmarksTuples, out

    def faceRotation(self, routesCrd, landmarksTuples, out):
        delta_y = abs(landmarksTuples[44][1] - landmarksTuples[38][1])
        delta_x = abs(landmarksTuples[44][0] - landmarksTuples[38][0])
        angle = np.arctan2(delta_y, delta_x)
        angle_degrees = np.degrees(angle)

        (h, w) = out.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, -angle_degrees, 1.0)
        rotated = cv2.warpAffine(out, M, (w, h))

        x_min, x_max = min(pt[0] for pt in routesCrd), max(pt[0] for pt in routesCrd)
        y_min, y_max = min(pt[1] for pt in routesCrd), max(pt[1] for pt in routesCrd)
        face_img = rotated[y_min:y_max, x_min:x_max]

        return face_img

    def faceRepresentation(self, face_img):
        if face_img is None:
            raise ValueError("Invalid image input - None. Please provide a valid image.")
        try:
            representation = DeepFace.represent(face_img, detector_backend='retinaface', model_name='ArcFace')
            return representation[0]['embedding']
        except Exception as e:
            print(f"Error in faceRepresentation: {e}")
            return None

# 모델 인스턴스 생성
model = CombinedFaceModel()
model.eval()  # 추론 모드로 설정

# 더미 입력 생성
dummy_input = torch.randn(1, 3, 320, 320)  # (배치 크기, 채널 수, 높이, 너비)

# ONNX로 변환
torch.onnx.export(
    model,
    dummy_input,
    "combined_face_model.onnx",
    input_names=['img'],
    output_names=['embedding'],
    dynamic_axes={'img': {0: 'batch_size'}},
    operator_export_type=torch.onnx.OperatorExportTypes.ONNX_ATEN_FALLBACK,
    do_constant_folding=True
)