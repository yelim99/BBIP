from utils.utils import faceAlignment, faceDetection, faceRepresentation, faceRotation, verifyFace
import cv2
import numpy as np
import threading
import time

cap = cv2.VideoCapture(0)
verifyFace_path = 'img.jpg'
verifyFaceImg = cv2.imread(verifyFace_path)

verified = []
detectedVerifiedFace = faceDetection(verifyFaceImg)[0]
routesCrd, landmarksTuples, out = faceAlignment(verifyFaceImg, detectedVerifiedFace)
verifiedFace = faceRotation(routesCrd, landmarksTuples, out)
vv = faceRepresentation(verifiedFace)
verified.append(vv)

def process_frame(frame):
    global cnt  # 전역 변수 사용 선언
    global sum
    start_time = time.time()  # 시작 시간 측정
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    faces = faceDetection(rgb_frame)

    if faces is None or len(faces) == 0:
        return frame

    for face in faces:
        routesCrd, landmarksTuples, out = faceAlignment(rgb_frame, face)
        rotated = faceRotation(routesCrd, landmarksTuples, out)
        if rotated is None:
            continue
        embedding = faceRepresentation(rotated)

        if not verifyFace(embedding, verified):
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

    return frame

capture_count = 0  # 캡처된 이미지 수를 세기 위한 변수
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 프레임 리사이즈 (속도 향상을 위해)
    frame = cv2.resize(frame, (640, 480))

    # 프레임 처리 스레드
    processed_frame = threading.Thread(target=process_frame, args=(frame,))
    processed_frame.start()
    processed_frame.join()

    cv2.imshow('Face Detection with Blur', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    elif 0xFF == ord('c'):  # 'c' 키를 눌러 캡처
            capture_count += 1
            filename = f"capture_{capture_count}.png"
            cv2.imwrite(filename, frame)  # 현재 프레임 저장
            print(f"Captured: {filename}")

cap.release()
cv2.destroyAllWindows()
