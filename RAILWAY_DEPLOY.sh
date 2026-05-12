#!/bin/bash

# 색상 정의
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}   메타도어 점검 앱 - Railway 배포 가이드${NC}"
echo -e "${BLUE}================================================${NC}\n"

echo -e "${YELLOW}📋 사전 확인 사항:${NC}"
echo "1. GitHub 계정이 있는가?"
echo "2. Railway 계정이 있는가? (https://railway.app)"
echo "3. Git이 설치되어 있는가?"
echo ""

read -p "위 세 가지가 모두 준비되었는가? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}준비가 필요합니다. GitHub와 Railway 가입을 먼저 완료하세요.${NC}"
    exit 1
fi

echo -e "\n${GREEN}✓ 준비 완료!${NC}\n"

# Step 1: Git 초기화
echo -e "${YELLOW}📍 Step 1: Git 저장소 초기화${NC}"
echo "================================================"

if [ -d ".git" ]; then
    echo "이미 Git 저장소가 있습니다."
else
    git init
    git config user.email "metadoor@example.com"
    git config user.name "MetaDoor Admin"
    git add .
    git commit -m "Initial commit: MetaDoor inspection system"
    echo -e "${GREEN}✓ Git 저장소 생성 완료${NC}"
fi

echo ""

# Step 2: GitHub 저장소 생성 안내
echo -e "${YELLOW}📍 Step 2: GitHub에 저장소 생성${NC}"
echo "================================================"
echo -e "${BLUE}다음 단계를 수행하세요:${NC}"
echo ""
echo "1️⃣  https://github.com/new 접속"
echo "2️⃣  Repository name: metadoor-inspection"
echo "3️⃣  Description: MetaDoor Maintenance Inspection System"
echo "4️⃣  Public 선택"
echo "5️⃣  'Create repository' 클릭"
echo ""
echo -e "${YELLOW}그 후 다음 명령어를 실행하세요:${NC}"
echo -e "${BLUE}git remote add origin https://github.com/YOUR-USERNAME/metadoor-inspection.git${NC}"
echo -e "${BLUE}git push -u origin main${NC}"
echo ""

read -p "GitHub에 업로드를 완료했는가? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}GitHub 업로드를 먼저 완료한 후 다시 실행하세요.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ GitHub 업로드 완료${NC}\n"

# Step 3: Railway 배포
echo -e "${YELLOW}📍 Step 3: Railway 배포${NC}"
echo "================================================"
echo -e "${BLUE}다음 단계를 수행하세요:${NC}"
echo ""
echo "1️⃣  https://railway.app 접속"
echo "2️⃣  GitHub 계정으로 로그인"
echo "3️⃣  'New Project' 클릭"
echo "4️⃣  'Deploy from GitHub repo' 선택"
echo "5️⃣  metadoor-inspection 저장소 선택"
echo "6️⃣  'Deploy' 클릭"
echo ""
echo -e "${YELLOW}배포가 시작됩니다 (약 2-3분 소요)${NC}"
echo ""

read -p "Railway 배포를 시작했는가? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Railway 배포를 먼저 시작하세요.${NC}"
    exit 1
fi

echo ""

# Step 4: 환경 변수 설정
echo -e "${YELLOW}📍 Step 4: 환경 변수 설정${NC}"
echo "================================================"
echo -e "${BLUE}Railway 대시보드에서:${NC}"
echo ""
echo "1️⃣  프로젝트 선택"
echo "2️⃣  'Variables' 탭 클릭"
echo "3️⃣  'Add Variable' 클릭"
echo ""
echo "다음 변수를 추가하세요:"
echo -e "${BLUE}변수명: SECRET_KEY${NC}"
echo -e "${BLUE}값: ${NC}$(openssl rand -hex 32)"
echo ""
echo "4️⃣  'Save' 클릭"
echo "5️⃣  'Redeploy' 클릭"
echo ""

read -p "환경 변수 설정을 완료했는가? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}환경 변수 설정을 완료하세요.${NC}"
    exit 1
fi

echo ""

# Step 5: 배포 완료
echo -e "${YELLOW}📍 Step 5: 배포 확인${NC}"
echo "================================================"
echo -e "${BLUE}Railway 대시보드에서:${NC}"
echo ""
echo "1️⃣  'Deployments' 탭 확인"
echo "2️⃣  초록색 체크마크 확인 (배포 성공)"
echo "3️⃣  'Settings' → 'Domains' 에서 공용 URL 확인"
echo ""
echo -e "${GREEN}생성된 공용 URL:${NC}"
echo -e "${BLUE}https://metadoor-inspection-[random].up.railway.app${NC}"
echo ""

# Step 6: 테스트
echo -e "${YELLOW}📍 Step 6: 로그인 테스트${NC}"
echo "================================================"
echo -e "${BLUE}생성된 URL에 접속하여 로그인하세요:${NC}"
echo ""
echo "아이디:   ${YELLOW}test${NC}"
echo "비밀번호: ${YELLOW}test${NC}"
echo ""

echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}🎉 배포 완료!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo -e "✅ 메타도어 점검 앱이 클라우드에 배포되었습니다!"
echo ""
echo "🌐 공용 주소: 위의 Railway Domains에서 확인"
echo "📱 모바일에서도 접속 가능"
echo "🔐 로그인: test / test"
echo ""
echo "💡 팁:"
echo "   - 팀원과 URL을 공유하면 모두 접속 가능"
echo "   - 코드 수정 후 git push하면 자동 배포"
echo "   - Railway 대시보드에서 Logs 확인 가능"
echo ""
