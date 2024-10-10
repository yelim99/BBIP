from fastapi import APIRouter
from apis import face_proportion_logo_license

# 라우터를 연결해주는 역할
api_router = APIRouter()
api_router.include_router(face_proportion_logo_license.router, prefix="/rtc", tags=["rtc"])
api_router.include_router(face_proportion_logo_license.router, prefix="/logo", tags=["logo"])
