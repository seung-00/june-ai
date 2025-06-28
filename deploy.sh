#!/bin/bash

# 환경변수 설정 (실제 값으로 변경 필요)
PROJECT_ID="decent-destiny-463614-g6"
REGION="us-central1"  # 서울 리전
REPOSITORY="flask-app-repo"
IMAGE_NAME="flask-hello-world"
SERVICE_NAME="flask-hello-world-service"
SERVICE_ACCOUNT="vertex-ai-accessor@decent-destiny-463614-g6.iam.gserviceaccount.com"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 Flask 앱을 GCP에 배포합니다...${NC}"

# 1. Docker 이미지 빌드 (AMD64 플랫폼으로)
echo -e "${YELLOW}📦 Docker 이미지를 빌드합니다...${NC}"
docker buildx build --platform linux/amd64 -t $IMAGE_NAME .

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Docker 빌드 실패${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker 이미지 빌드 완료${NC}"

# 2. Artifact Registry에 태그
echo -e "${YELLOW}🏷️  이미지에 태그를 추가합니다...${NC}"
docker tag $IMAGE_NAME $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE_NAME

# 3. Artifact Registry에 푸시
echo -e "${YELLOW}📤 Artifact Registry에 이미지를 푸시합니다...${NC}"
docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE_NAME

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 이미지 푸시 실패${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 이미지 푸시 완료${NC}"

# 4. Cloud Run에 배포 (서비스 계정 명시)
echo -e "${YELLOW}☁️  Cloud Run에 서비스를 배포합니다...${NC}"
gcloud run deploy $SERVICE_NAME \
    --image $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8080 \
    --memory 512Mi \
    --cpu 1 \
    --max-instances 10 \
    --service-account=$SERVICE_ACCOUNT

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Cloud Run 배포 실패${NC}"
    exit 1
fi

echo -e "${GREEN}🎉 배포 완료!${NC}"
echo -e "${YELLOW}📋 다음 명령어로 서비스 URL을 확인하세요:${NC}"
echo "gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)'"

curl "https://flask-hello-world-service-698010238719.us-central1.run.app/health" 