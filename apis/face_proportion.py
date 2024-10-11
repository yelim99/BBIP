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
import collections
from aiortc.contrib.media import MediaPlayer, MediaRelay
from ultralytics import YOLO
import torch

if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

router = APIRouter()

# 기본 설정
ROOT = os.path.dirname(__file__)
logging.basicConfig(level=logging.INFO)
pcs = set()
relay = MediaRelay()

# 프레임 카운터 및 FPS 체크를 위한 변수
frame_count = 0
fps_start_time = time.perf_counter()

# 전역 FFmpeg 프로세스
ffmpeg_process = None

# 버퍼 크기 설정
VIDEO_BUFFER_SIZE = 60  # 비디오 버퍼에 저장할 프레임 수
AUDIO_BUFFER_SIZE = 60  # 오디오 버퍼에 저장할 샘플 수

# 버퍼 초기화
video_buffer = collections.deque(maxlen=VIDEO_BUFFER_SIZE)
audio_buffer = collections.deque(maxlen=AUDIO_BUFFER_SIZE)

if torch.cuda.is_available():
    device = torch.device("cuda")
    print("GPU 사용 가능:", torch.cuda.get_device_name(0))
else:
    device = torch.device("cpu")
    print("GPU 사용 불가능, CPU로 실행")

# 모델 불러오기
model = YOLO("model/face_detection_yolo.engine")

# 추적기 리스트
trackers = []
tracker_labels = []

# 프레임 카운터 및 FPS 체크를 위한 변수
frame_count = 0
fps_start_time = time.perf_counter()

class MediaTransformTrack(MediaStreamTrack):

    def __init__(self, track, kind):
        super().__init__()
        self.track = track
        self.kind = kind
        self.is_processing = False

         # FFmpeg 명령어 설정
        ffmpeg_command = [
            'ffmpeg', '-re',
            '-f', 'rawvideo',
            '-pixel_format', 'bgr24',
            '-video_size', '640x480',  # 비디오 크기 설정
            '-r', '15',
            '-i', '-',  # stdin에서 입력받음
            '-f', 'lavfi',
            '-i', 'anullsrc=r=44100:cl=stereo',
            '-c:v', 'libx264',
            '-b:v', '1500k',  # 비디오 비트레이트
            '-c:a', 'aac',  # 오디오 코덱 설정 (빈 오디오를 aac로 인코딩
            '-b:a', '128k',  # 오디오 비트레이트
            '-preset', 'veryfast',
             '-maxrate', '3000k',
             '-bufsize', '6000k',
            '-pix_fmt', 'yuv420p',
            '-g', '30',
            '-vf', 'scale=360:640',
            '-f', 'flv',
            'rtmp://a.rtmp.youtube.com/live2/ujj9-6fa7-9xy9-04w7-09bs'  # YouTube RTMP URL과 스트림 키 설정
        ]

        # FFmpeg 프로세스를 시작
        self.ffmpeg_process = subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE)
        print('송출')


    async def recv(self):
        global frame_count, fps_start_time  # 글로벌 변수 사용
        global model, known_face_embeddings, known_face_names, trackers, tracker_faces
        
        frame = await self.track.recv()

        if self.kind == "video":

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

            processing_start_time = time.perf_counter()
            # VideoFrame을 YUV420P 형식의 NumPy 배열로 변환
            image = frame.to_ndarray(format="yuv420p")
            # YUV420P에서 BGR로 변환
            image_bgr = cv2.cvtColor(image, cv2.COLOR_YUV2BGR_I420)
            
            
            if frame_count % 20 == 0 or len(trackers) == 0:
            
                # 모델 예측
                detection = model(image_bgr)[0]
                object_boxes = []     # 한 프레임 내에서 검출된 객체들
                trackers = []       # 추적기

                for data in detection.boxes.data.tolist():
                    confidence = float(data[4])
                    if confidence < 0.6:
                        continue

                    xmin, ymin, xmax, ymax = int(data[0]), int(data[1]), int(data[2]), int(data[3])
                    w = xmax - xmin
                    h = ymax - ymin
                    object_boxes.append((xmin, ymin, w, h))

                # YOLO로 감지된 얼굴에 대해 CSRT 추적기 추가
                for (xmin, ymin, w, h) in object_boxes:
                    # 추적된 객체 부분을 잘라냄
                    object_region = image_bgr[ymin:ymin+h, xmin:xmin+w]
                    if object_region.size > 0:
                        tracker = cv2.TrackerCSRT_create()
                        tracker.init(image_bgr, (xmin, ymin, w, h))
                        name = "face" #얼굴이면 추적기에 face로 등록해놓음
                        trackers.append((tracker, (xmin,ymin,w,h),object_region.size, name))
                            
            # 넓이에 따라 내림차순 정렬
            trackers.sort(key=lambda x: x[2], reverse=True)  # object region를 기준으로 정렬
            
            target_selected = False

            # 추적된 객체들 업데이트
            for i, (tracker, bbox, object_region, label) in enumerate(trackers): 
                ret, bbox = tracker.update(image_bgr)
                if ret:
                    (xmin, ymin, w, h) = [int(v) for v in bbox]
                    xmax = xmin + w
                    ymax = ymin + h
                    
                    # 이름 표시
                    #cv2.putText(image_bgr, label, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                    # 얼굴 부분을 원형으로 블러 처리
                    if(target_selected==False):
                        target_selected = True
                    elif object_region > 0:
                        mask = np.zeros_like(image_bgr)
                        center = (xmin + w // 2, ymin + h // 2)
                        radius = int(min(w, h) / 2)
                        cv2.circle(mask, center, radius + 10, (255, 255, 255), -1)

                        # 블러 처리된 이미지를 생성하고 원형 마스크를 적용하여 블러 처리
                        blurred_img = cv2.GaussianBlur(image_bgr, (21, 21), 20)
                        image_bgr = np.where(mask == (255, 255, 255), blurred_img, image_bgr)
            self.is_processing = True
            print("비디오 변환 처리")

            processing_end_time = time.perf_counter()
            print(f"모델 처리 시간: {processing_end_time - processing_start_time:.4f} 초")
            
            new_frame_start_time = time.perf_counter()
            new_frame = VideoFrame.from_ndarray(image_bgr, format="bgr24")
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
            # FFmpeg 프로세스로 처리된 프레임 전달
            # image_bgr= image_bgr.reshape(640,480)
            print(image_bgr.shape)
            # 비디오 데이터가 올바른 형식인지 확인
            # if image_bgr.shape[0] != 480 or image_bgr.shape[1] != 640 or image_bgr.dtype != np.uint8:
            #     print("비디오 데이터 형식이 올바르지 않습니다.")
            #     image_bgr= cv2.resize(image_bgr, (480, 640))
            # # img_bgr= cv2.resize(img_bgr, (480, 640))
            # # print(image_bgr.shape)
            # self.ffmpeg_process.stdin.write(image_bgr.tobytes())
            if image_bgr.shape[0] != 480 or image_bgr.shape[1] != 640 or image_bgr.dtype != np.uint8:
                print("비디오 데이터 형식이 올바르지 않습니다.")
                print(f"현재 형상: {image_bgr.shape}, 현재 데이터 유형: {image_bgr.dtype}")
                image_bgr = cv2.resize(image_bgr, (640, 480))  # 올바른 크기로 조정

            # 비디오 데이터가 올바른 형식인지 확인
            if image_bgr.shape[0] == 480 and image_bgr.shape[1] == 640 and image_bgr.dtype == np.uint8:
                print("비디오 데이터 형식이 올바릅니다.")
                self.ffmpeg_process.stdin.write(image_bgr.tobytes())
            else:
                print("비디오 데이터 형식이 여전히 올바르지 않습니다.")

            return new_frame
        
        elif self.kind == "audio":
            #print("오디오 처리 중")
            audio_data = frame.to_ndarray()
            audio_buffer.append(audio_data)
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
    #client_id = str(uuid.uuid4())
    #await websocket.send_text(json.dumps({"client_id": client_id}))

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

                elif message.get("type") == "candidate":
                    candidate = message["candidate"]
                    print('candidate:', candidate['candidate'])
                    ip = candidate['candidate'].split(' ')[4]
                    port = candidate['candidate'].split(' ')[5]
                    protocol = candidate['candidate'].split(' ')[7]
                    priority = candidate['candidate'].split(' ')[3]
                    foundation = candidate['candidate'].split(' ')[0]
                    component = candidate['candidate'].split(' ')[1]
                    type = candidate['candidate'].split(' ')[7]
                    rtc_candidate = RTCIceCandidate(
                        ip=ip,
                        port=port,
                        protocol=protocol,
                        priority=priority,
                        foundation=foundation,
                        component=component,
                        type=type,
                        sdpMid=candidate['sdpMid'],
                        sdpMLineIndex=candidate['sdpMLineIndex']
                    )
                    await pc.addIceCandidate(rtc_candidate)
        except WebSocketDisconnect:
            #print(f"Client disconnected: {client_id}")
            pcs.remove(pc)
            break
        except Exception as e:
            print(f"An error occurred: {e}")