from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apis.apis_base import api_router
from fastapi.staticfiles import StaticFiles
import os
import uvicorn

# 모든 origin에서 발생하는 요청들 처리함
def include_cors(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

def include_router(app):
    app.include_router(api_router)

def start_application():
    app = FastAPI(title="BBIP", version="1.0")
    include_cors(app)
    include_router(app)
    
    # 정적 파일 서빙
    root_directory = os.path.join(os.getcwd(), "static")  # 현재 작업 디렉토리에 있는 static 폴더
    app.mount("/static", StaticFiles(directory=root_directory), name="static")
    
    return app

app = start_application()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, ws_ping_interval=600, ws_ping_timeout=60)