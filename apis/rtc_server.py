import argparse
import asyncio
import json
import logging
import os
import ssl
import uuid
from fastapi.responses import HTMLResponse
import logging
import time

import cv2
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer, MediaRelay
from av import VideoFrame
from fastapi import APIRouter
from utils import blur_yolo as yolo
from ultralytics import YOLO


router = APIRouter()


# 기본 설정
ROOT = os.path.dirname(__file__)
logger = logging.getLogger("pc")
pcs = set()
relay = MediaRelay()
model = YOLO('../model/facedetection_yolo.pt')

class VideoTransformTrack(MediaStreamTrack):
    kind = "video"
    # 모델 로드
    global model
    

    def __init__(self, track, transform):
        super().__init__()
        self.track = track
        self.transform = transform

    async def recv(self):
        logging.info("비디오 변환 처리")
        start_time = time.time()
        frame = await self.track.recv()
        img = frame.to_ndarray(format="bgr24")
        img = yolo.process_frame(img, model)
        end_time = time.time()
        print(f"YOLO 처리 시간: {end_time - start_time} 초")
        
        new_frame = VideoFrame.from_ndarray(img, format="bgr24")
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
    pcs[offer['client_id']]= pc


    @pc.on("icecandidate")
    async def on_icecandidate(event):
        if event.candidate:
            await WebSocket.send_text(json.dumps({"candidate": event.candidate.to_json()}))
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
            pc.addTrack(VideoTransformTrack(track, 'rotate'))

    while True:
        try:
            data = await websocket.receive_text()
            message = json.loads(data)

            if "sdp" in message:
                # sdp가 문자열인지 확인
                sdp = message["sdp"]
                if isinstance(sdp, str):
                    await pc.setRemoteDescription(RTCSessionDescription(sdp=sdp, type=message["type"]))
                    
                    answer = await pc.createAnswer()
                    await pc.setLocalDescription(answer)
                    
                    # 클라이언트에게 응답 전송
                    await websocket.send_text(json.dumps({"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}))
                else:
                    print(f"Received SDP is not a string: {sdp}")  # 잘못된 SDP 형식 로그

        except WebSocketDisconnect:
            print(f"Client disconnected: {client_id}")
            pcs.remove(pc)
            break
        except Exception as e:
            print(f"An error occurred: {e}")  # 일반 오류 처리
