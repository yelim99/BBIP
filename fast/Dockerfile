# 1. Python 3.9 버전의 slim 이미지를 사용
FROM python:3.7

# 2. 작업 디렉토리 설정
WORKDIR /app

RUN apt-get clean && apt-get update && apt-get install -y libgl1-mesa-glx
# 3. requirements.txt 파일을 Docker 이미지에 복사
COPY requirements.txt .

# 4. 필요한 패키지들을 설치
RUN pip install --no-cache-dir -r requirements.txt

# 5. 소스 코드를 컨테이너에 복사
COPY . .

# 6. FastAPI 서버 실행 (uvicorn을 사용)
CMD ["uvicorn", "face-recognition:app", "--host", "0.0.0.0", "--port", "8000"]
