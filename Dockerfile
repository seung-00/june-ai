# Python 3.11 slim 이미지 사용 (스프링의 openjdk:17-slim과 비슷)
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사 (모든 Python 파일)
COPY *.py .

# 포트 노출 (Cloud Run은 동적으로 PORT 환경변수 사용)
EXPOSE 8080

# 환경변수 설정
ENV PYTHONUNBUFFERED=1

# Flask 내장 서버로 앱 실행
CMD ["python", "app.py"] 