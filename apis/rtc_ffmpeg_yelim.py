import argparse
import asyncio
import json
import logging
import os
import sys
import ssl
import uuid
from fastapi.responses import HTMLResponse
import time
import subprocess

import cv2
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer, MediaRelay
from av import VideoFrame
from fastapi import APIRouter
from utils import blur_yolo as yolo

router = APIRouter()

# 기본 설정
ROOT = os.path.dirname(__file__)
logger = logging.getLogger("pc")
pcs = set()
relay = MediaRelay()

# 전역 FFmpeg 프로세스
ffmpeg_process = None

# 로그 레벨을 ERROR로 설정하여 불필요한 정보성 로그 비활성화
logging.getLogger().setLevel(logging.ERROR)
model = yolo.load_model()

# FFmpeg 프로세스를 시작하는 함수
def start_ffmpeg_process():
    global ffmpeg_process
    if ffmpeg_process is None:
        ffmpeg_command = [
            'ffmpeg', '-re',
            '-loglevel', 'debug',
            '-f', 'rawvideo',
            '-pixel_format', 'bgr24',
            '-video_size', '480x640',  # 비디오 크기 설정
            '-r', '30',
            '-i', '-',  # stdin에서 비디오 입력
            '-f', 's16le',  # 오디오 입력 포맷을 설정
            '-ar', '44100',  # 샘플링 레이트
            '-ac', '2',      # 스테레오 채널
            # '-i', 'pipe:1',  # stdin에서 오디오 입력
            '-c:v', 'libx264',
            '-b:v', '1500k',  # 비디오 비트레이트
            '-c:a', 'aac',    # 오디오 코덱 설정
            '-b:a', '128k',   # 오디오 비트레이트
            # '-async', '1',
            '-vsync', '1',
            '-preset', 'fast',
            '-fflags', '+nobuffer',
            # '-maxrate', '2000k',
            '-bufsize', '2400k',
            '-pix_fmt', 'yuv420p',
            '-g', '60',
            '-f', 'flv',
            'rtmp://a.rtmp.youtube.com/live2/sj16-j2mx-gff2-t3d9-464e'  
            # YouTube RTMP URL과 스트림 키 설정 (맨 뒤 슬래시 다음이 스트림 키)
        ]
        ffmpeg_process = subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE)
        print('FFmpeg 프로세스 시작')


class MediaTransformTrack(MediaStreamTrack):
    global model

    def __init__(self, track, kind):
        super().__init__()
        self.track = track
        self.kind = kind

        # FFmpeg 프로세스 시작
        start_ffmpeg_process()

    async def recv(self):
        frame = await self.track.recv()
        
        if self.kind == "video":
            print("비디오 변환 처리")
            img = frame.to_ndarray(format="bgr24")

            # OpenCV에서 일정한 간격으로 프레임 처리
            start_time = time.time()    
            img = yolo.process_frame(img, model)
            elapsed_time = time.time() - start_time

            # FPS에 맞춰 다음 프레임 처리까지 대기
            time.sleep(max(1./30 - elapsed_time, 0))

            # FFmpeg로 비디오 프레임 전달
            ffmpeg_process.stdin.write(img.tobytes())  # 전역 ffmpeg_process 사용

            new_frame = VideoFrame.from_ndarray(img, format="bgr24")
            new_frame.pts = frame.pts
            new_frame.time_base = frame.time_base
            return new_frame

        elif self.kind == "audio":
            print("오디오 처리 중")
            audio_data = frame.to_ndarray()  # 오디오 데이터를 NumPy 배열로 변환
            ffmpeg_process.stdin.write(audio_data.tobytes())  # 전역 ffmpeg_process 사용
            return frame

    def __del__(self):
        # FFmpeg 프로세스 종료
        global ffmpeg_process
        if ffmpeg_process:
            ffmpeg_process.stdin.close()
            ffmpeg_process.wait()
            ffmpeg_process = None


@router.get("/", response_class=HTMLResponse)
async def index():
    with open(os.path.join(ROOT, "..\\static\\index.html"), encoding='utf-8') as f:
        return f.read()


@router.post("/offer")
async def offer(offer: RTCSessionDescription):
    logging.info("offer 요청 수신")
    pc = RTCPeerConnection()
    pcs.add(pc)
    pcs[offer['client_id']] = pc

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

    logging.info("ws 요청")
    await websocket.accept()
    client_id = str(uuid.uuid4())
    await websocket.send_text(json.dumps({"client_id": client_id}))

    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("icecandidate")
    async def on_icecandidate(event):
        logging.info("candidate")
        if event.candidate:
            await websocket.send_text(json.dumps({"candidate": event.candidate.to_json()}))

    @pc.on("track")
    def on_track(track):
        logging.info(f"트랙 수신: {track.kind}")
        if track.kind == "video":
            pc.addTrack(MediaTransformTrack(track, 'video'))
        elif track.kind == "audio":
            pc.addTrack(MediaTransformTrack(track, 'audio'))

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
