from utils.utils import FaceProcessor
import cv2
import numpy as np
import threading
import time

# FaceProcessor 클래스 인스턴스화
face_processor = FaceProcessor()

# 얼굴 검증을 위한 이미지 로드 및 처리
verifyFace_path = 'img.jpg'
verifyFaceImg = cv2.imread(verifyFace_path)
detectedVerifiedFace = face_processor.faceDetection(verifyFaceImg)[0]
routesCrd, landmarksTuples, out = face_processor.faceAlignment(verifyFaceImg, detectedVerifiedFace)
verifiedFace = face_processor.faceRotation(routesCrd, landmarksTuples, out)
verified_embedding = face_processor.faceRepresentation(verifiedFace)
verified = [verified_embedding]

def process_frame(frame, verified):
    start_time = time.time()  # 시작 시간 측정
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    faces = face_processor.faceDetection(rgb_frame)

    if faces is None or len(faces) == 0:
        return frame

    for face in faces:
        routesCrd, landmarksTuples, out = face_processor.faceAlignment(rgb_frame, face)
        rotated = face_processor.faceRotation(routesCrd, landmarksTuples, out)
        if rotated is None:
            continue
        embedding = face_processor.faceRepresentation(rotated)

        if not face_processor.verifyFace(embedding, verified):
            continue
        else:
            routesCrd = np.array(routesCrd)
            selected_points = routesCrd[:18]
            x_coords = selected_points[:, 0]
            y_coords = selected_points[:, 1]
            x1, x2 = int(np.min(x_coords)), int(np.max(x_coords))
            y1, y2 = int(np.min(y_coords)), int(np.max(y_coords))
            face_region = frame[y1:y2, x1:x2]
            blurred_face = cv2.GaussianBlur(face_region, (15, 15), 100)
            frame[y1:y2, x1:x2] = blurred_face

    end_time = time.time()  # 종료 시간 측정
    latency = end_time - start_time  # 지연 시간 계산
    print(f"Processing latency: {latency:.4f} seconds")  # 지연 시간 출력
    return frame

# 웹캠 열기
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 프레임 리사이즈 (속도 향상을 위해)
    frame = cv2.resize(frame, (640, 480))

    # 프레임 처리 스레드
    processed_frame = threading.Thread(target=process_frame, args=(frame, verified))
    processed_frame.start()
    processed_frame.join()

    cv2.imshow('Face Detection with Blur', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
