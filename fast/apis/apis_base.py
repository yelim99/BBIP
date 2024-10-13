from fastapi import APIRouter
from apis import face_proportion_logo_license, logo_license, face_proportion, no_blur, weapon, face_weapon,gstreamertest

# 라우터를 연결해주는 역할
api_router = APIRouter()
api_router.include_router(no_blur.router,prefix="/noblur", tags=["noblur"])
api_router.include_router(face_proportion_logo_license.router, prefix="/face_text", tags=["face_text"])
api_router.include_router(logo_license.router, prefix="/text", tags=["text"])
api_router.include_router(face_proportion.router, prefix="/face", tags=["face"])
api_router.include_router(weapon.router, prefix="/weapon", tags=["weapon"])
api_router.include_router(face_weapon.router, prefix="/face_weapon", tags=["face_weapon"])
#api_router.include_router(gstreamertest.router, prefix="/gs",tags=["gs"])
