import argparse
import asyncio
import json
import logging
import os
import subprocess
import time
import uuid
import numpy as np
from tensorflow.python.keras import models
import cv2
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription, RTCIceCandidate
from av import VideoFrame
from fastapi import APIRouter
from utils import blur_yolo as modelutil
from utils import recognize_face as recogFace
import collections
from ultralytics import YOLO

import torch

if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

router = APIRouter()

# 기본 설정
ROOT = os.path.dirname(__file__)
logging.basicConfig(level=logging.INFO)
pcs = set()

# 프레임 카운터 및 FPS 체크를 위한 변수
frame_count = 0
fps_start_time = time.perf_counter()


# 버퍼 크기 설정
VIDEO_BUFFER_SIZE = 60  # 비디오 버퍼에 저장할 프레임 수
AUDIO_BUFFER_SIZE = 60  # 오디오 버퍼에 저장할 샘플 수

# 버퍼 초기화
video_buffer = collections.deque(maxlen=VIDEO_BUFFER_SIZE)
audio_buffer = collections.deque(maxlen=AUDIO_BUFFER_SIZE)
import torch
torch.cuda.get_device_name(0)	#gpu 확인
torch.cuda.is_available()
# GPU 사용 설정
if torch.cuda.is_available():
    device = torch.device("cuda")
    print("GPU 사용 가능:", torch.cuda.get_device_name(0))
else:
    device = torch.device("cpu")
    print("GPU 사용 불가능, CPU로 실행")


model2 = YOLO('../model/logo_license_detection_yolo.pt')
model2.to(device)



class VideoTransformTrack(MediaStreamTrack):
    kind = "video"

    def __init__(self, track, transform):
        super().__init__()
        self.track = track
        self.transform = transform
        self.is_processing = False

    async def recv(self):
        global frame_count, fps_start_time  # 글로벌 변수 사용
        global model, known_face_embeddings, known_face_names, trackers, tracker_faces


        start_time = time.perf_counter()  # 시작 시간 기록

        if self.is_processing:
            print("현재 프레임 처리 중, 이번 프레임 패스")
            return await self.track.recv()

        self.is_processing = True
        print("비디오 변환 처리")

        frame_start_time = time.perf_counter()
        frame = await self.track.recv()
        frame_end_time = time.perf_counter()
        print(f"프레임 수신 시간: {frame_end_time - frame_start_time:.4f} 초")

        #img_conversion_start_time = time.perf_counter()
        #img = yolo.process_frame(img, model)
        #img = frame.to_ndarray(format="bgr24")
        #img_conversion_end_time = time.perf_counter()
        #print(f"프레임 변환 시간: {img_conversion_end_time - img_conversion_start_time:.4f} 초")

        processing_start_time = time.perf_counter()
        # VideoFrame을 YUV420P 형식의 NumPy 배열로 변환
        image = frame.to_ndarray(format="yuv420p")
        # YUV420P에서 BGR로 변환
        image_bgr = cv2.cvtColor(image, cv2.COLOR_YUV2BGR_I420)
        
    
        img = modelutil.process_frame(image_bgr, model2)
        processing_end_time = time.perf_counter()
        print(f"모델 처리 시간: {processing_end_time - processing_start_time:.4f} 초")
        
        new_frame_start_time = time.perf_counter()
        new_frame = VideoFrame.from_ndarray(img, format="bgr24")
        new_frame.pts = frame.pts
        print(f"현재 프레임 frame.pts: {frame.pts}")
        new_frame.time_base = frame.time_base
        print(f"현재 프레임 time_base: {frame.time_base}")
        new_frame_end_time = time.perf_counter()
        print(f"새 프레임 생성 시간: {new_frame_end_time - new_frame_start_time:.4f} 초")
        print(f"fps: {modelutil.calculate_fps(start_time)}")
        # 프레임 수 증가
        frame_count += 1

        # FPS 계산
        if time.perf_counter() - fps_start_time >= 1.0:  # 1초마다 FPS 계산
            fps = frame_count / (time.perf_counter() - fps_start_time)
            print(f"현재 FPS: {fps:.2f}")
            frame_count = 0  # 카운터 초기화
            fps_start_time = time.perf_counter()  # 시간 초기화

        self.is_processing = False
        total_time = time.perf_counter() - start_time
        print(f"총 처리 시간: {total_time:.4f} 초")
        return new_frame

@router.get("/", response_class=HTMLResponse)
async def index():
    with open(os.path.join(ROOT, "..\\static\\index.html"), encoding='utf-8') as f:
        return f.read()

    @pc.on("icecandidate")
    async def on_icecandidate(event):
        if event.candidate:
            # Send the ICE candidate to the client (using WebSocket or HTTP)
            pass

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return {
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    }

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    print("ws 요청")
    await websocket.accept()
    # client_id = str(uuid.uuid4())
    # await websocket.send_text(json.dumps({"client_id": client_id}))

    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("icecandidate")
    async def on_icecandidate(event):
        print("candidate")
        if event.candidate:
            await websocket.send_text(json.dumps({"candidate": event.candidate.to_json()}))

    @pc.on("track")
    def on_track(track):
        print("비디오 수신")
        if track.kind == "video":
            pc.addTrack(VideoTransformTrack(track, 'rotate'))

    while True:
        try:
            data = await websocket.receive_text()
            message = json.loads(data)
            print(message)

            if "sdp" in message:
                print('sdp in message')
                sdp = message["sdp"]
                if isinstance(sdp, str):
                    await pc.setRemoteDescription(RTCSessionDescription(sdp=sdp, type=message["type"]))
                    
                    answer = await pc.createAnswer()
                    await pc.setLocalDescription(answer)
                    
                    await websocket.send_text(json.dumps({"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}))
                else:
                    print(f"Received SDP is not a string: {sdp}")

            elif message.get('action') == 'toggle_camera':
                print("Camera toggle action received")
                for sender in pc.getSenders():
                    if sender.track.kind == 'video':
                        await pc.removeTrack(sender)

        except WebSocketDisconnect:
            # print(f"Client disconnected: {client_id}")
            pcs.remove(pc)
            break
        except Exception as e:
            print(f"An error occurred: {e}")