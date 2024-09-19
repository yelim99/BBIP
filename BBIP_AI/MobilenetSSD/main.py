import utils.detect as detect
from utils.util import faceAlignment, faceRepresentation, faceRotation, verifyFace
import tensorflow.lite as tflite
import cv2
import os
import time
import numpy as np

interpreter = tflite.Interpreter(
    os.path.join(os.getcwd(), "ssd_mobilenet_v2_face_quant_postprocess.tflite")
)
interpreter.allocate_tensors()
verifyFace_path = 'img.jpg'
image = cv2.imread(verifyFace_path)
verified = []
# 이미지 원본 크기 저장
original_height, original_width = image.shape[:2]

scale_x = original_width / 320
scale_y = original_height / 320

# 이미지 리사이즈
image_resized = cv2.resize(image, dsize=(320, 320), interpolation=cv2.INTER_AREA)

# 입력 텐서 준비
tensor = detect.input_tensor(interpreter=interpreter)
tensor[:, :] = image_resized  # 이미지 복사
del tensor
interpreter.invoke()  # 추론 시작

objs = detect.get_output(interpreter, 0.5, (scale_x, scale_y))
bbox = objs[0].bbox
xmin = int(bbox.xmin * scale_x)
xmax = int(bbox.xmax * scale_x)
ymin = int(bbox.ymin * scale_y)
ymax = int(bbox.ymax * scale_y)
face = [xmin, ymin, xmax, ymax]

routesCrd, landmarksTuples, out = faceAlignment(image_resized, face)
rotated = faceRotation(routesCrd, landmarksTuples, out)
vv = faceRepresentation(rotated)
verified.append(vv)

def apply_blur(frame, objs, scale_x, scale_y, verified):

    for obj in objs:
        bbox = obj.bbox
        xmin = int(bbox.xmin * scale_x)
        xmax = int(bbox.xmax * scale_x)
        ymin = int(bbox.ymin * scale_y)
        ymax = int(bbox.ymax * scale_y)
        
        # 얼굴 부분 추출
        face = [xmin,ymin, xmax,ymax]
        routesCrd, landmarksTuples, out = faceAlignment(frame, face)
        routesCrd = np.array(routesCrd, dtype=np.int32)

        print(type(routesCrd))  # numpy 배열인지 확인
        print(routesCrd.shape)  # 형태 확인

        
        mask = np.zeros_like(frame, dtype=np.uint8)
        cv2.fillConvexPoly(mask, routesCrd, (255, 255, 255))  # 다각형으로 얼굴 영역 채우기

        # 얼굴 영역만 추출
        face_region = cv2.bitwise_and(frame, mask)

        embedding = faceRepresentation(face_region)
        if embedding is None:
            continue

        if not verifyFace(embedding, verified):
            continue
        else:
            routesCrd = np.array(routesCrd)
            # y좌표 추출
            y_coords = routesCrd[:, 1] 
            # y좌표의 최소값과 최대값 계산
            y1 = int(np.min(y_coords))
            y2 = int(np.max(y_coords))
            # 37번 점부터 46번 점까지의 x좌표 추출
            x_coords = routesCrd[17:, 0]
            # x좌표의 최소값과 최대값 계산
            x1 = int(np.min(x_coords))
            x2 = int(np.max(x_coords))
            face_region = frame[y1:y2, x1:x2]
            blurred_face = cv2.GaussianBlur(face_region, (15, 15), 100)
            frame[y1:y2, x1:x2] = blurred_face
    
    return frame

def main():
    cap = cv2.VideoCapture(0)
    capture_count = 0  # 캡처된 이미지 수를 세기 위한 변수
    global cnt  # 전역 변수 사용 선언
    global sum
    cnt=0
    sum=0
    
    while True:
        start_time = time.time()  # 시작 시간 측정
        ret, image = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
        # 이미지 원본 크기 저장
        original_height, original_width = image.shape[:2]

        scale_x = original_width / 320
        scale_y = original_height / 320

        # 이미지 리사이즈
        image_resized = cv2.resize(image, dsize=(320, 320), interpolation=cv2.INTER_AREA)

        # 입력 텐서 준비
        tensor = detect.input_tensor(interpreter=interpreter)
        tensor[:, :] = image_resized  # 이미지 복사
        del tensor
        interpreter.invoke()  # 추론 시작
        
        objs = detect.get_output(interpreter, 0.5, (scale_x, scale_y))
        image = apply_blur(image_resized, objs=objs, scale_x=scale_x, scale_y=scale_y, verified=[])
        del objs
        image_origin_size = cv2.resize(image, dsize=(original_width, original_height), interpolation=cv2.INTER_AREA)
        cv2.imshow('face detector', image_origin_size)
        end_time = time.time()
        print(end_time-start_time)
        sum+=end_time-start_time
        cnt+=1
        print(sum/cnt)
        k = cv2.waitKey(30) & 0xff
        if k == 27:  # ESC 키를 눌러 종료
            break

    cap.release()
    cv2.destroyAllWindows()
    
if __name__ == '__main__':
    main()