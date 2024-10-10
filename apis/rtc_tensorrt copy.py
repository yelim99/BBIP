import argparse
import asyncio
import json
import logging
import os
import ssl
import uuid
import time

import cv2
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer, MediaRelay
from av import VideoFrame
from fastapi import APIRouter
import tensorrt as trt
import pycuda.driver as cuda
import pycuda.autoinit  # CUDA 초기화

router = APIRouter()

# 기본 설정
ROOT = os.path.dirname(__file__)
logger = logging.getLogger("pc")
pcs = set()
relay = MediaRelay()

# TensorRT 엔진 로드 함수
def load_engine(engine_file_path):
    with open(engine_file_path, 'rb') as f:
        engine_data = f.read()
    runtime = trt.Runtime(trt.Logger(trt.Logger.WARNING))
    engine = runtime.deserialize_cuda_engine(engine_data)
    return engine

# 입력, 출력 버퍼 및 컨텍스트 할당 함수
def allocate_buffers(engine):
    inputs = []
    outputs = []
    bindings = []
    stream = cuda.Stream()
    for binding in engine:
        size = trt.volume(engine.get_binding_shape(binding)) * engine.max_batch_size
        dtype = trt.nptype(engine.get_binding_dtype(binding))
        buffer = cuda.mem_alloc(size * np.dtype(dtype).itemsize)
        bindings.append(int(buffer))
        if engine.binding_is_input(binding):
            inputs.append(buffer)
        else:
            outputs.append(buffer)
    return inputs, outputs, bindings, stream

# TensorRT 추론 함수
def do_inference(context, bindings, inputs, outputs, stream):
    cuda.memcpy_htod_async(inputs[0], input_data, stream)
    context.execute_async_v2(bindings=bindings, stream_handle=stream.handle)
    cuda.memcpy_dtoh_async(output_data, outputs[0], stream)

# 여러 엔진 파일 관리
class EngineManager:
    def __init__(self, engine_paths):
        self.engines = {}
        self.contexts = {}
        for path in engine_paths:
            engine = load_engine(path)
            self.engines[path] = engine
            self.contexts[path] = engine.create_execution_context()

    def get_engine(self, path):
        return self.engines.get(path)

    def get_context(self, path):
        return self.contexts.get(path)

# 엔진 파일 경로 리스트
engine_file_paths = [
    '../model/face_detection_yolo.pt',
    'model/facenet_keras.h5',
    '../model/logo_license_detection_yolo.pt'
]
engine_manager = EngineManager(engine_file_paths)

class VideoTransformTrack(MediaStreamTrack):
    kind = "video"

    def __init__(self, track, engine_path):
        super().__init__()
        self.track = track
        self.engine_path = engine_path
        self.engine = engine_manager.get_engine(engine_path)
        self.context = engine_manager.get_context(engine_path)
        self.inputs, self.outputs, self.bindings, self.stream = allocate_buffers(self.engine)

    async def recv(self):
        logging.info("비디오 변환 처리")
        start_time = time.time()
        frame = await self.track.recv()
        img = frame.to_ndarray(format="bgr24")

        # 프레임 전처리
        input_data = cv2.resize(img, (640, 640)).astype(np.float32)  # 엔진 입력 크기로 조정
        input_data = input_data.transpose((2, 0, 1))  # HWC -> CHW
        input_data = np.expand_dims(input_data, axis=0)  # 배치 차원 추가

        # TensorRT 추론 실행
        cuda.memcpy_htod(self.inputs[0], input_data)
        self.context.execute_async_v2(bindings=self.bindings, stream_handle=self.stream.handle)
        cuda.memcpy_dtoh(self.outputs[0], output_data)

        end_time = time.time()
        print(f"TensorRT 처리 시간: {end_time - start_time} 초")

        new_frame = VideoFrame.from_ndarray(output_data, format="bgr24")
        new_frame.pts = frame.pts
        new_frame.time_base = frame.time_base
        return new_frame

@router.get("/", response_class=HTMLResponse)
async def index():
    with open(os.path.join(ROOT, "..\\static\\index.html"), encoding='utf-8') as f:
        return f.read()

@router.post("/offer")
async def offer(offer: RTCSessionDescription):
    logging.info("offer 요청 수신")
    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("icecandidate")
    async def on_icecandidate(event):
        if event.candidate:
            await websocket.send_text(json.dumps({"candidate": event.candidate.to_json()}))
            print("send on_icecandidate")

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return {
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    }

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    logging.info("ws 요청")
    await websocket.accept()
    client_id = str(uuid.uuid4())
    await websocket.send_text(json.dumps({"client_id": client_id}))

    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("candidate")
    async def on_icecandidate(event):
        logging.info("candidate")
        if event.candidate:
            print("send on_icecandidate")
            await websocket.send_text(json.dumps({"candidate": event.candidate.to_json()}))

    @pc.on("track")
    def on_track(track):
        logging.info("비디오 수신")
        if track.kind == "video":
            # 엔진 파일 경로에 따라 동적으로 VideoTransformTrack 인스턴스 생성
            pc.addTrack(VideoTransformTrack(track, '../model/facedetection_yolo.engine'))  # 또는 다른 엔진 파일 경로

    while True:
        try:
            data = await websocket.receive_text()
            message = json.loads(data)

            if "sdp" in message:
                sdp = message["sdp"]
                if isinstance(sdp, str):
                    await pc.setRemoteDescription(RTCSessionDescription(sdp=sdp, type=message["type"]))
                    
                    answer = await pc.createAnswer()
                    await pc.setLocalDescription(answer)
                    
                    await websocket.send_text(json.dumps({"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}))
                else:
                    print(f"Received SDP is not a string: {sdp}")

        except WebSocketDisconnect:
            print(f"Client disconnected: {client_id}")
            pcs.remove(pc)
            break
        except Exception as e:
            print(f"An error occurred: {e}")

# FastAPI 앱 설정
app = FastAPI()
app.include_router(router)
