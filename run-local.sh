#!/bin/bash
# 메타도어 점검 앱 - 로컬 테스트 스크립트

echo "🚀 메타도어 점검 앱 로컬 테스트 시작"
echo "=================================="

# 1. 의존성 설치
echo "1️⃣ Python 라이브러리 설치 중..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ 설치 완료"
else
    echo "❌ 설치 실패"
    exit 1
fi

# 2. 환경 변수 설정
echo ""
echo "2️⃣ 환경 변수 설정 중..."
export FLASK_APP=app.py
export FLASK_ENV=development
export SECRET_KEY="dev-secret-key-local-testing"

echo "✅ 환경 변수 설정 완료"

# 3. 서버 실행
echo ""
echo "3️⃣ Flask 서버 시작 중..."
echo "📍 접속 주소: http://localhost:5000"
echo ""
echo "⏹️  종료하려면: Ctrl+C"
echo "=================================="

python app.py
