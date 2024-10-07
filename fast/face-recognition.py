import datetime
import cv2
import numpy as np
from tensorflow.keras.models import load_model
from ultralytics import YOLO
from fastapi import FastAPI, HTTPException, Response  # Response 추가
import requests  # requests 라이브러리 추가
from pydantic import BaseModel

app = FastAPI()

# FaceNet 모델 로드 (GPU 사용)
print("Loading FaceNet model...")
facenet_model = load_model('./facenet_keras.h5')
print("FaceNet model loaded successfully.")

# YOLO 모델 설정 (더 가벼운 YOLO 모델 사용)
print("Loading YOLO model...")
model = YOLO('./best.pt')
print("YOLO model loaded successfully.")

# 얼굴 임베딩(벡터)을 추출하는 함수
def get_face_embedding(model, face_pixels):
    face_pixels = cv2.resize(face_pixels, (160, 160))  # FaceNet 입력 크기로 맞춤
    face_pixels = face_pixels.astype('float32')
    mean, std = face_pixels.mean(), face_pixels.std()
    if std == 0:  # 표준편차가 0인 경우 예외 처리
        std = 1e-6
    face_pixels = (face_pixels - mean) / std
    face_pixels = np.expand_dims(face_pixels, axis=0)
    embedding = model.predict(face_pixels)
    return embedding[0]


class ImageRequest(BaseModel):
    image_url: str

@app.post("/process-image")
async def process_image(request: ImageRequest):
    try:
        image_url = request.image_url
        print(f"Fetching image from URL: {image_url}")
        # 이미지 URL에서 이미지 다운로드
        response = requests.get(image_url)
        if response.status_code != 200:
            print(f"Failed to fetch image from URL: {image_url}")
            raise HTTPException(status_code=400, detail="Image not found in the provided URL")
        
        # 이미지를 numpy 배열로 변환
        print("Converting image to numpy array...")
        image_array = np.frombuffer(response.content, np.uint8)
        img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        # YOLO로 얼굴 감지
        print("Running YOLO detection...")
        detection = model(img)
        face_embedding = None

        print("Processing detection results...")
        if len(detection[0].boxes) > 0:
            for data in detection[0].boxes.data.tolist():
                xmin, ymin, xmax, ymax = map(int, data[:4])  # 신뢰도 값을 제외한 좌표 추출
                print(f"Detected face at coordinates: ({xmin}, {ymin}), ({xmax}, {ymax})")
                face_region = img[ymin:ymax, xmin:xmax]
                face_embedding = get_face_embedding(facenet_model, face_region)
                break  # 첫 번째 얼굴에 대해서만 임베딩 추출
        else:
            print("No faces detected in the image.")
            raise HTTPException(status_code=404, detail="No face detected")
        
        # 추출한 임베딩을 바이너리로 변환
        print("Converting face embedding to bytes...")
        face_embedding_bytes = np.array(face_embedding, dtype=np.float32).tobytes()

        # 바이너리 데이터 반환
        print("Returning face embedding as binary data.")
        return Response(content=face_embedding_bytes, media_type="application/octet-stream")

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
