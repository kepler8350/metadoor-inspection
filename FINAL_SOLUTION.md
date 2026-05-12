# 메타도어 점검 앱 - Railway 배포 최종 솔루션

## 🔴 현재 문제
- URL: https://web-production-e1e4f.up.railway.app
- 오류: "Application failed to respond"
- 원인: 기존 서비스 배포 오류 상태 (복구 불가능)

## ✅ 해결책: 서비스 재생성

### Step 1: 기존 서비스 삭제
1. https://railway.app/dashboard 접속
2. "refreshing-connection" 프로젝트 클릭
3. "web" 서비스 선택
4. 우측 상단 **3점 메뉴 (...)**  클릭
5. **"Delete Service"** 선택 → 확인

### Step 2: 새로운 서비스 생성
1. 프로젝트 홈 → **"+ Add"** 또는 **"New"** 버튼
2. **"GitHub Repository"** 선택
3. **kepler8350/metadoor-inspection** 저장소 선택
4. **"Deploy"** 클릭
5. 3-5분 대기

### Step 3: 배포 확인
- Deployments 탭에서 상태를 "ACTIVE" 확인
- "Deployment successful" 메시지 확인

### Step 4: 접속
- 새로운 URL 확인 (도메인이 변경될 수 있음)
- 또는 Settings → Networking에서 공용 도메인 확인
- 로그인: test / test

---

## 📦 현재 배포된 코드

### app.py
```python
import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello World! MetaDoor is running!'

@app.route('/health')
def health():
    return 'OK'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f'Starting Flask on port {port}', flush=True)
    app.run(host='0.0.0.0', port=port, debug=False)
```

### Procfile
```
web: python app.py
```

### requirements.txt
```
Flask==2.3.2
```

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir Flask==2.3.2

COPY app.py .

ENV PORT=5000
EXPOSE 5000

CMD ["sh", "-c", "python app.py"]
```

---

## 📊 GitHub 저장소
https://github.com/kepler8350/metadoor-inspection

최신 커밋: 906046e - Fix Dockerfile: Use sh -c for proper environment variable handling

---

## 🎯 목표
✅ 기본 Flask 앱으로 배포 성공 확인
✅ 이후 HTML/CSS/JS 추가 가능
✅ 메타도어 점검 시스템 완성

---

**⚠️ 중요: 위의 Step 1-4를 꼭 따라주세요!**
기존 서비스는 복구 불가능한 상태이므로 재생성이 필수입니다.
