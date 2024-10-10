from ultralytics import YOLO
import os
import logging

# 로그 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

os.environ["CUDA_VISIBLE_DEVICES"] = "0"  # 첫 번째 GPU 사용

# YOLO 모델 로드
model = YOLO('model/logo_license_detection_yolo.pt')

try:
    # 모델을 TensorRT 엔진으로 변환
    logging.info("모델을 TensorRT 엔진으로 변환 중...")
    model.export(format='engine', device='0')  # GPU 장치 번호를 문자열로 지정
    logging.info("모델 변환 성공: 엔진 파일이 생성되었습니다.")
except Exception as e:
    logging.error("모델 변환 중 오류 발생: %s", e)


#https://docs.ultralytics.com/ko/integrations/tensorrt/#configuring-int8-export
#https://wjs7347.tistory.com/71s