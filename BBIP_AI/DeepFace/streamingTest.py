from utils.utils import faceAlignment, faceDetection, faceRepresentation
import cv2
import numpy as np

cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 그레이스케일 변환
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 얼굴 인식
    faces = faceDetection(gray_frame)

     # 인식된 얼굴에 블러 처리
    for face in faces:
        routesCrd, landmarksTuples, out = faceAlignment(gray_frame, face)


       # routesCrd가 리스트라면 NumPy 배열로 변환
        routesCrd = np.array(routesCrd)  # routesCrd를 NumPy 배열로 변환

        # 1부터 18번 점까지만 사용
        selected_points = routesCrd[:18]  # 0부터 시작하므로 0~17번 인덱스 사용

        # x와 y 좌표의 최소값과 최대값을 계산하여 경계 박스 생성
        x_coords = selected_points[:, 0]
        y_coords = selected_points[:, 1]

        x1, x2 = int(np.min(x_coords)), int(np.max(x_coords))
        y1, y2 = int(np.min(y_coords)), int(np.max(y_coords))

        # 얼굴 영역을 blur 처리
        face_region = frame[y1:y2, x1:x2]
        blurred_face = cv2.GaussianBlur(face_region, (15, 15), 0)

        # 원래 프레임에 블러 처리된 얼굴 영역 업데이트
        frame[y1:y2, x1:x2] = blurred_face

    # 결과 출력
    cv2.imshow('Face Detection with Blur', frame)

    # 'q' 키를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 비디오 캡처 종료
cap.release()
cv2.destroyAllWindows()
