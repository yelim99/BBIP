import argparse
import asyncio
import json
import logging
import os
import subprocess
import uuid
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription, RTCIceCandidate
from av import VideoFrame
from fastapi import APIRouter
from utils import blur_yolo as yolo
import collections
from ultralytics import YOLO

if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

router = APIRouter()

# 기본 설정
ROOT = os.path.dirname(__file__)
logging.basicConfig(level=logging.INFO)
pcs = set()

# 전역 FFmpeg 프로세스
ffmpeg_process = None

# 버퍼 크기 설정
VIDEO_BUFFER_SIZE = 60  # 비디오 버퍼에 저장할 프레임 수
AUDIO_BUFFER_SIZE = 60  # 오디오 버퍼에 저장할 샘플 수

# 버퍼 초기화
video_buffer = collections.deque(maxlen=VIDEO_BUFFER_SIZE)
audio_buffer = collections.deque(maxlen=AUDIO_BUFFER_SIZE)

# 모델 불러오기
model = YOLO('../model/face_detection_yolo.pt')
model2 = YOLO('../model/logo_license_detection_yolo.pt')

async def start_ffmpeg_process():
    global ffmpeg_process
    if ffmpeg_process is None:
        ffmpeg_command = [
            'ffmpeg', '-re',
            '-loglevel', 'debug',
            '-f', 'rawvideo',
            '-pixel_format', 'bgr24',
            '-video_size', '640x480',
            '-r', '30',
            '-i', 'pipe:0',
            '-f', 's16le',  # 오디오 입력 포맷을 설정
            '-ar', '44100', # 샘플링 레이트
            '-ac', '2',     # 스테레오 채널
            '-i', 'pipe:1',
            '-c:v', 'libx264',
            '-b:v', '1500k',    # 비디오 비트레이트
            '-c:a', 'aac',      # 오디오 코덱 설정
            '-bufsize', '1500k',
            '-b:a', '128k',     # 오디오 비트레이트
            '-preset', 'fast',
            '-pix_fmt', 'yuv420p',
            '-g', '60',
            '-f', 'flv',
            'rtmp://a.rtmp.youtube.com/live2/t7fx-gb4z-stjk-q22h-8mt2'
            # YouTube RTMP URL과 스트림 키 설정 (맨 뒤 슬래시 다음이 스트림 키)       
        ]
        
        ffmpeg_process = await asyncio.create_subprocess_exec(
            *ffmpeg_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        #print('FFmpeg 프로세스 시작')
        asyncio.create_task(log_ffmpeg_output(ffmpeg_process))

async def log_ffmpeg_output(process):
    while True:
        output = await process.stderr.read(100)
        if not output:
            break
        #print(output.decode())

async def send_to_ffmpeg():
    global ffmpeg_process
    while ffmpeg_process:
        await asyncio.sleep(0.1)  # 0.1초 간격으로 확인
        #print(f"Video buffer size: {len(video_buffer)}")  # 버퍼사이즈 확인
        #print(f"Audio buffer size: {len(audio_buffer)}")
        # 비디오 데이터 전송
        while video_buffer:
            frame = video_buffer.popleft()
            ffmpeg_process.stdin.write(frame.tobytes())
            await ffmpeg_process.stdin.drain()

        # 오디오 데이터 전송
        while audio_buffer:
            frame = audio_buffer.popleft()
            ffmpeg_process.stdin.write(frame.tobytes())
            await ffmpeg_process.stdin.drain()

        #print("FFmpeg에 데이터 전송 중...")
        
        if ffmpeg_process.returncode is not None:
            #print('FFmpeg 프로세스가 종료되었습니다.')
            break

class MediaTransformTrack(MediaStreamTrack):
    global model

    def __init__(self, track, kind):
        super().__init__()
        self.track = track
        self.kind = kind

        # FFmpeg 프로세스 시작
        asyncio.create_task(start_ffmpeg_process())

    async def recv(self):
        frame = await self.track.recv()
        
        if self.kind == "video":
            #print("비디오 변환 처리")
            img = frame.to_ndarray(format="bgr24")
            img = yolo.process_frame(img, model)

            # 버퍼에 비디오 프레임 추가
            video_buffer.append(img)

            new_frame = VideoFrame.from_ndarray(img, format="bgr24")
            new_frame.pts = frame.pts
            new_frame.time_base = frame.time_base
            return new_frame

        elif self.kind == "audio":
            #print("오디오 처리 중")
            audio_data = frame.to_ndarray()
            audio_buffer.append(audio_data)
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
    client_id = str(uuid.uuid4())
    pc = RTCPeerConnection()
    # STUN/TURN 서버 설정
    pc._ice_servers = [
        {
            'urls': 'stun:stun.l.google.com:19302'  # STUN 서버
        },
        {
            'urls': 'turn:j11a203.p.ssafy.io',  # TURN 서버
            'username': 'username',  # TURN 서버 사용자 이름
            'credential': 'password'  # TURN 서버 비밀번호
        }
    ]

    pcs.add(pc)

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return {
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type,
        "status" :  "Offer received"
    }

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    logging.info("ws 요청")
    await websocket.accept()
    client_id = str(uuid.uuid4())
    await websocket.send_text(json.dumps({"client_id": client_id}))

    pc = RTCPeerConnection()
    # STUN/TURN 서버 설정
    pc._ice_servers = [
        {
            'urls': 'stun:stun.l.google.com:19302'  # STUN 서버
        },
        {
            'urls': 'turn:j11a203.p.ssafy.io',  # TURN 서버
            'username': 'username',  # TURN 서버 사용자 이름
            'credential': 'password'  # TURN 서버 비밀번호
        }
    ]
    pcs.add(pc)

    @pc.on("icecandidate")
    async def on_icecandidate(event):
        print("candidate")
        if event.candidate:
            await websocket.send_text(json.dumps({"candidate": event.candidate.to_json()}))

    @pc.on("iceconnectionstatechange")
    async def on_ice_connection_state_change():
        state = pc.iceConnectionState
        logging.info(f"ICE Connection State: {state}")
        if state == "connected":
            logging.info("Connection established!")

    @pc.on("track")
    def on_track(track):
        logging.info(f"트랙 수신: {track.kind}")
        if track.kind == "video":
            pc.addTrack(MediaTransformTrack(track, 'video'))
        elif track.kind == "audio":
            pc.addTrack(MediaTransformTrack(track, 'audio'))

    # FFmpeg 전송 시작
    asyncio.create_task(send_to_ffmpeg())

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

            # ICE candidate 수신 및 추가
            # 웹소켓에서 수신한 메세지에 candidate가 포함되어 있으면 이를 RTCIceCandidate 객체로 변환한 후, pc.addIceCandidate(candidate)를 호출하여 후보를 추가함
            if "candidate" in message:
                logging.info("icecandidate")
                candidate_info = message["candidate"]
                # component 변환
                if candidate_info['component'] == "rtp":
                    c = 1
                elif candidate_info['component'] == "rtcp":
                    c = 2 
                candidate = RTCIceCandidate(
                    component=c,
                    foundation=candidate_info['foundation'],
                    ip=candidate_info['address'],
                    port=candidate_info['port'],
                    priority=candidate_info['priority'],
                    protocol=candidate_info['protocol'],
                    type=candidate_info['type'],
                    sdpMid=candidate_info['sdpMid'],
                    tcpType=candidate_info['tcpType'],
                    sdpMLineIndex=candidate_info["sdpMLineIndex"]  # 클라이언트에서 보낸 sdpMLineIndex 값
                )
                await pc.addIceCandidate(candidate)

        except WebSocketDisconnect:
            #print(f"Client disconnected: {client_id}")
            pcs.remove(pc)
            break
        except Exception as e:
            print(f"An error occurred: {e}")