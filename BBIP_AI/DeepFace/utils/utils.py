import cv2
from deepface import DeepFace
import torch
from facenet_pytorch import MTCNN
import dlib
import numpy as np
from matplotlib import pyplot as plt
from scipy.spatial.distance import cosine


def faceDetection(image):
    # MTCNN 모델 초기화
    mtcnn = MTCNN(keep_all=True, device='cuda' if torch.cuda.is_available() else 'cpu')
    
    # BGR 이미지를 RGB로 변환
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # 얼굴 검출
    boxes, _ = mtcnn.detect(image_rgb)
    return boxes


def faceAlignment(img, face):
    baseImg = img.copy()

    dlib_box = dlib.rectangle(int(face[0]), int(face[1]), int(face[2]), int(face[3]))
    
    landmarkDetector = dlib.shape_predictor("utils/shape_predictor_68_face_landmarks.dat")
    landmarks=landmarkDetector(img,dlib_box)
    landmarksTuples = []
    for i in range(0,68):
        x = landmarks.part(i).x
        y = landmarks.part(i).y
        landmarksTuples.append((x,y))
        cv2.circle(baseImg,(x,y),2,(255,255,255),-1)
    
    routes = [i for i in range(16,-1,-1)] + [i for i in range(17,26+1)] +[16]
    routesCrd = []
    baseImg = img.copy()
    for i in range(0, len(routes)-1):
        sourcePoint = routes[i]
        targetPoint = routes[i+1]

        sourceCrd = landmarksTuples[sourcePoint]
        targetCrd = landmarksTuples[targetPoint]

        routesCrd.append(sourceCrd)
        cv2.line(baseImg, sourceCrd, targetCrd, (255,255,255), 2)

    routesCrd = routesCrd + [routesCrd[0]]
    mask = np.zeros((img.shape[0], img.shape[1]), dtype=np.uint8)
    mask = cv2.fillConvexPoly(mask, np.array(routesCrd, np.int32), 1)
    mask = mask.astype(np.bool_)
    out = np.zeros_like(img)
    
    # 얼굴 부분만 추출
    out[mask] = img[mask]
    return routesCrd, landmarksTuples, out

def faceRotation(routesCrd, landmarksTuples, out):
     # 회전 각도 계산
    delta_y = abs(landmarksTuples[44][1] - landmarksTuples[38][1])
    delta_x = abs(landmarksTuples[44][0] - landmarksTuples[38][0])
    angle = np.arctan2(delta_y, delta_x)
    angle_degrees = np.degrees(angle)

    # 이미지 회전
    (h, w) = out.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, -angle_degrees, 1.0)
    rotated = cv2.warpAffine(out, M, (w, h), flags=cv2.INTER_CUBIC)

    # 얼굴 부분의 경계 박스 구하기
    x_min = min([pt[0] for pt in routesCrd])
    x_max = max([pt[0] for pt in routesCrd])
    y_min = min([pt[1] for pt in routesCrd])
    y_max = max([pt[1] for pt in routesCrd])
    
    # 원본 경계 박스 좌표
    box_points = np.array([
        [x_min, y_min],
        [x_max, y_min],
        [x_max, y_max],
        [x_min, y_max]
    ], dtype='float32')

    # 회전 변환 적용
    rotated_box_points = cv2.transform(np.array([box_points]), M)[0]

    # 회전된 경계 박스의 새로운 최대/최소 좌표 계산
    x_rotated = rotated_box_points[:, 0]
    y_rotated = rotated_box_points[:, 1]

    x_min_rotated = int(np.min(x_rotated))
    x_max_rotated = int(np.max(x_rotated))
    y_min_rotated = int(np.min(y_rotated))
    y_max_rotated = int(np.max(y_rotated))

    # 이미지에서 얼굴 부분 잘라내기
    face_img = rotated[y_min_rotated:y_max_rotated, x_min_rotated:x_max_rotated]
    
    return face_img
    
def faceRepresentation(face_img):
    return DeepFace.represent(face_img, detector_backend='retinaface', model_name='ArcFace')[0].get('embedding')

def verifyFace(face, verified):
    threshold=0.4   # 임계값 0.4로 두고 테스트
    min_distance = float('inf')
    for embedding in verified:
        distance = cosine(face, embedding)
        if distance < min_distance:
            min_distance = distance
    print(min_distance)
    return min_distance>threshold