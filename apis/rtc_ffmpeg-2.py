import argparse
import asyncio
import json
import logging
import os
import sys
import ssl
import uuid
from fastapi.responses import HTMLResponse
import logging
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
# 로그 레벨을 ERROR로 설정하여 불필요한 정보성 로그 비활성화
logging.getLogger().setLevel(logging.ERROR)
model = yolo.load_model()

# class VideoTransformTrack(MediaStreamTrack):
#     global model

#     def __init__(self, track, transform):
#         super().__init__()
#         self.track = track
#         self.transform = transform
#         self.ffmpeg_process = None

#         # FFmpeg 명령어 설정
#         ffmpeg_command = [
#             'ffmpeg', '-re',
#             '-f', 'rawvideo',
#             '-pixel_format', 'bgr24',
#             '-video_size', '640x480',  # 비디오 크기 설정
#             '-r', '30',
#             '-i', '-',  # stdin에서 입력받음
#             # '-f', 'lavfi',
#             # '-i', 'anullsrc=r=44100:cl=stereo',
#             '-f', 's16le',  # 오디오 입력 포맷을 설정
#             '-ar', '44100',  # 샘플링 레이트
#             '-ac', '2',      # 스테레오 채널
#             '-i', 'pipe:1',  # 파이프를 통해 오디오 입력받음
#             '-c:v', 'libx264',
#             '-b:v', '1500k',  # 비디오 비트레이트
#             '-c:a', 'aac',  # 오디오 코덱 설정 (빈 오디오를 aac로 인코딩
#             '-b:a', '128k',  # 오디오 비트레이트
#             '-preset', 'fast',
#             '-maxrate', '2000k',
#             '-bufsize', '4000k',
#             '-pix_fmt', 'yuv420p',
#             '-g', '60',
#             '-f', 'flv',
#             'rtmp://a.rtmp.youtube.com/live2/sj16-j2mx-gff2-t3d9-464e'  # YouTube RTMP URL과 스트림 키 설정
#         ]

#         # FFmpeg 프로세스를 시작
#         self.ffmpeg_process = subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE)
#         print('송출')

#     async def recv(self):
#         logging.info("비디오 변환 처리")
#         frame = await self.track.recv()
#         img = frame.to_ndarray(format="bgr24")

#         # 로그 레벨을 ERROR로 설정하여 불필요한 정보성 로그 비활성화
#         logging.getLogger().setLevel(logging.ERROR)
#         img = yolo.process_frame(img, model)

#         # print(img.shape)  # 예시: (480, 640, 3)

#         # FFmpeg 프로세스로 처리된 프레임 전달
#         self.ffmpeg_process.stdin.write(img.tobytes())

#         new_frame = VideoFrame.from_ndarray(img, format="bgr24")
#         new_frame.pts = frame.pts
#         new_frame.time_base = frame.time_base
#         return new_frame

#     def __del__(self):
#         # FFmpeg 프로세스 종료
#         if self.ffmpeg_process:
#             self.ffmpeg_process.stdin.close()
#             self.ffmpeg_process.wait()


# class AudioTransformTrack(MediaStreamTrack):
#     kind = "audio"  # 오디오 트랙 지정

#     # def __init__(self, track):
#     #     super().__init__()
#     #     self.track = track

#     def __init__(self, track, ffmpeg_process):
#         super().__init__()
#         self.track = track
#         self.ffmpeg_process = ffmpeg_process  # ffmpeg_process를 인자로 받아 저장


#     async def recv(self):
#         frame = await self.track.recv()  # 오디오 프레임 수신
#         audio_data = frame.to_ndarray()  # 오디오 데이터를 NumPy 배열로 변환
        
#         # FFmpeg로 오디오 데이터를 전달
#         self.ffmpeg_process.stdin.write(audio_data.tobytes())
#         return frame

# ffmpeg_process = None

class MediaTransformTrack(MediaStreamTrack):
    global model

    def __init__(self, track, kind):
        super().__init__()
        self.track = track
        self.kind = kind  # 비디오와 오디오를 구분하는 kind 값 설정
        self.ffmpeg_process = None  # FFmpeg 프로세스를 받음

        # if self.kind == "video":
            # FFmpeg 비디오 처리 명령어 설정 (필요시 추가 설정)
        ffmpeg_command = [
            'ffmpeg', '-re',
            '-f', 'rawvideo',
            '-pixel_format', 'bgr24',
            '-video_size', '480x640',  # 비디오 크기 설정
            '-r', '30',
            '-i', '-',  # stdin에서 입력받음
            '-f', 's16le',  # 오디오 입력 포맷을 설정
            '-ar', '44100',  # 샘플링 레이트
            '-ac', '2',      # 스테레오 채널
            # '-i', 'pipe:1',  # 파이프를 통해 오디오 입력받음
            '-c:v', 'libx264',
            '-b:v', '1500k',  # 비디오 비트레이트
            '-c:a', 'aac',    # 오디오 코덱 설정
            '-b:a', '128k',   # 오디오 비트레이트
            '-preset', 'fast',
            # '-fflags', '+nobuffer', # 이거 한 번 주석해제하고 해봐바!!
            # '-maxrate', '2000k',
            # '-bufsize', '4000k',
            '-pix_fmt', 'yuv420p',
            '-g', '60',
            '-f', 'flv',
            'rtmp://a.rtmp.youtube.com/live2/sj16-j2mx-gff2-t3d9-464e'  # YouTube RTMP URL과 스트림 키 설정
        ]

        # FFmpeg 프로세스를 시작
        self.ffmpeg_process = subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE)
        print('비디오 송출 시작')

    async def recv(self):
        frame = await self.track.recv()
        
        if self.kind == "video":
            print("비디오 변환 처리")
            img = frame.to_ndarray(format="bgr24")

            # 표준 출력을 임시로 비활성화
            # sys.stdout = open(os.devnull, 'w')          

            img = yolo.process_frame(img, model)

            # 표준 출력 다시 활성화
            # sys.stdout = sys.__stdout__

            # FFmpeg 프로세스로 처리된 비디오 프레임 전달
            self.ffmpeg_process.stdin.write(img.tobytes())

            new_frame = VideoFrame.from_ndarray(img, format="bgr24")
            new_frame.pts = frame.pts
            new_frame.time_base = frame.time_base
            return new_frame

        elif self.kind == "audio":
            print("오디오 처리 중")
            audio_data = frame.to_ndarray()  # 오디오 데이터를 NumPy 배열로 변환

            # FFmpeg로 오디오 데이터를 전달
            self.ffmpeg_process.stdin.write(audio_data.tobytes())
            return frame

    def __del__(self):
        # FFmpeg 프로세스 종료
        if self.ffmpeg_process:
            self.ffmpeg_process.stdin.close()
            self.ffmpeg_process.wait()



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

    # @pc.on("track")
    # def on_track(track):
    #     logging.info("비디오 수신")
    #     if track.kind == "video":
    #         pc.addTrack(VideoTransformTrack(track, 'rotate'))
    #     elif track.kind == "audio":
    #         # pc.addTrack(track)  # 오디오 트랙도 추가
    #         # pc.addTrack(AudioTransformTrack(track))  # 오디오 트랙 처리
    #         pc.addTrack(AudioTransformTrack(track))  # 오디오 트랙 처리


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
