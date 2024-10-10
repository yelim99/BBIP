import cv2
import numpy as np
import os
import tensorrt as trt

# TensorRT 엔진 로드 함수
def load_engine(engine_file_path):
    with open(engine_file_path, 'rb') as f:
        engine_data = f.read()
    runtime = trt.Runtime(trt.Logger(trt.Logger.WARNING))
    engine = runtime.deserialize_cuda_engine(engine_data)
    print(os.path.exists(engine_file_path))
    if engine is None:
        raise ValueError(f"Failed to load engine from {engine_file_path}")
    return engine

# TensorRT 추론 함수
def infer(engine, input_data):
    context = engine.create_execution_context()
    bindings = []
    inputs = []
    outputs = []
    
    # 입력 및 출력 버퍼 할당
    input_shape = (1, 3, 640, 640)  # 예시로 YOLOv5의 입력 크기
    input_size = np.prod(input_shape)
    output_size = 8400  # 예시로 YOLOv5의 출력 크기
    input_buffer = np.empty(input_size, dtype=np.float32)
    output_buffer = np.empty(output_size, dtype=np.float32)
    
    # 바인딩 설정
    bindings.append(int(input_buffer.ctypes.data))
    bindings.append(int(output_buffer.ctypes.data))

    # 입력 데이터 준비
    input_data = cv2.resize(input_data, (640, 640))
    input_data = input_data.transpose((2, 0, 1))  # HWC -> CHW
    input_data = input_data[np.newaxis, :] / 255.0  # 정규화 및 배치 차원 추가
    np.copyto(input_buffer, input_data.ravel())

    # 추론 실행
    context.execute_v2(bindings=bindings)

    return output_buffer

# 웹캠에서 이미지 수신 및 객체 감지
def main():
    engine_file_path = "C:\\Users\\SSAFY\\Desktop\\git_fastapi\\S11P21A203\\model\\face_detection_yolo.engine"  # 엔진 파일 경로
    engine = load_engine(engine_file_path)

    cap = cv2.VideoCapture(0)  # 웹캠 열기

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        output = infer(engine, frame)

        # 경계 상자 그리기 (임의의 예시, 실제 구현 시 적절한 후처리 필요)
        for i in range(len(output) // 6):  # 예시로 6개 요소당 1개 객체
            x1, y1, x2, y2, conf, cls = output[i*6:i*6+6]
            if conf > 0.5:  # 신뢰도 기준
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                cv2.putText(frame, f'Class: {int(cls)}, Conf: {conf:.2f}', (int(x1), int(y1)-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        cv2.imshow('Webcam', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
