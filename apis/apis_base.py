from fastapi import APIRouter
from apis import face_proportion_logo_license, logo_license, face_proportion, no_blur

# 라우터를 연결해주는 역할
api_router = APIRouter()
api_router.include_router(no_blur.router,prefix="/noblur", tags=["noblur"])
api_router.include_router(face_proportion_logo_license.router, prefix="/face_text", tags=["face_text"])
api_router.include_router(logo_license.router, prefix="/text", tags=["text"])
api_router.include_router(face_proportion.router, prefix="/face", tags=["face"])