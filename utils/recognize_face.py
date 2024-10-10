import cv2
import numpy as np

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

# 얼굴 임베딩을 비교하는 함수 (L2 거리 사용)
def is_match(known_embedding, candidate_embedding, threshold=8.5):
    distance = np.linalg.norm(known_embedding - candidate_embedding)
    return distance < threshold

# 얼굴 등록 함수
def register_face(face_image, name, known_face_embeddings, known_face_names, facenet_model):
    face_embedding = get_face_embedding(facenet_model, face_image)
    known_face_embeddings.append(face_embedding)
    known_face_names.append(name)
    print(f'{name} 등록 완료')
