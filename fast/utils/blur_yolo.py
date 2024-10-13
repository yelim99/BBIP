import time
import cv2
from ultralytics import YOLO

def calculate_fps(start_time):
    """
    FPS를 계산하는 함수.
    
    :param start_time: 프레임 처리 시작 시간
    :return: FPS 값
    """
    end_time = time.perf_counter()
    total_time = end_time - start_time  # 두 시간을 float으로 계산
    fps = 1 / total_time if total_time > 0 else 0  # FPS 계산
    return fps
