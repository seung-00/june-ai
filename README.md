# Flask Hello World App

스프링 개발자를 위한 Python Flask 앱 예제입니다.

## 🏗️ 프로젝트 구조

```
.
├── app.py              # Flask 메인 애플리케이션 (스프링의 @RestController와 유사)
├── requirements.txt    # Python 의존성 (스프링의 pom.xml과 유사)
├── Dockerfile         # Docker 이미지 빌드 설정
├── deploy.sh          # GCP 배포 스크립트
└── README.md          # 프로젝트 문서
```

## 🚀 로컬 실행

### 1. Python 가상환경 생성 (선택사항)
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate     # Windows
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 앱 실행
```bash
python app.py
```

### 4. 테스트
```bash
curl http://localhost:8080/
# 응답: {"message": "Hello World!", "status": "success"}

curl http://localhost:8080/health
# 응답: {"status": "healthy", "service": "flask-app"}
```

## 🐳 Docker 로컬 테스트

```bash
# 이미지 빌드
docker build -t flask-hello-world .

# 컨테이너 실행
docker run -p 8080:8080 flask-hello-world

# 테스트
curl http://localhost:8080/
```

## ☁️ GCP 배포

### 사전 준비사항

1. **GCP 프로젝트 생성**
2. **gcloud CLI 설치 및 인증**
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```
3. **필요한 API 활성화**
   ```bash
   gcloud services enable artifactregistry.googleapis.com
   gcloud services enable run.googleapis.com
   ```
4. **Artifact Registry 리포지토리 생성**
   ```bash
   gcloud artifacts repositories create flask-app-repo \
     --repository-format=docker \
     --location=asia-northeast3 \
     --description="Flask app repository"
   ```

### 배포 실행

1. **deploy.sh 파일 수정**
   ```bash
   # deploy.sh 파일에서 PROJECT_ID를 실제 프로젝트 ID로 변경
   PROJECT_ID="your-actual-project-id"
   ```

2. **배포 스크립트 실행**
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

## 📚 스프링 vs Flask 비교

| 스프링 | Flask | 설명 |
|--------|-------|------|
| `@RestController` | `@app.route()` | REST API 엔드포인트 정의 |
| `pom.xml` | `requirements.txt` | 의존성 관리 |
| `@GetMapping("/")` | `@app.route('/')` | GET 요청 매핑 |
| `@ResponseBody` | `jsonify()` | JSON 응답 |
| `application.properties` | 환경변수 | 설정 관리 |
| JAR 파일 | Python 스크립트 | 실행 파일 |

## 🔧 주요 엔드포인트

- `GET /` - Hello World 메시지
- `GET /health` - 헬스 체크

## 💡 팁

- Flask는 스프링보다 가볍고 빠르게 시작할 수 있습니다
- `gunicorn`은 Python의 프로덕션 WSGI 서버입니다 (스프링의 내장 톰캣과 유사)
- Cloud Run은 서버리스 플랫폼으로, 트래픽에 따라 자동 스케일링됩니다 