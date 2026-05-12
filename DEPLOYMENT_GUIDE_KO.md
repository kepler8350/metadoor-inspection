# 🚀 Railway 배포 단계별 가이드

## 사전 준비
- GitHub 계정
- Railway 계정 (https://railway.app)
- Git 설치

---

## 📍 Step 1: GitHub에 코드 업로드

### 1.1 로컬에서 Git 초기화
```bash
cd /경로/metadoor-inspection
git init
git config user.email "your-email@example.com"
git config user.name "Your Name"
```

### 1.2 GitHub에 새 저장소 생성
1. https://github.com/new 접속
2. Repository name: `metadoor-inspection`
3. Public 선택
4. "Create repository" 클릭

### 1.3 로컬 코드를 GitHub에 업로드
```bash
git add .
git commit -m "Initial commit: MetaDoor inspection app"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/metadoor-inspection.git
git push -u origin main
```

---

## 🚂 Step 2: Railway에서 배포

### 2.1 Railway 접속 및 로그인
1. https://railway.app 접속
2. "Start Free" 또는 "Login" 클릭
3. GitHub으로 로그인

### 2.2 새 프로젝트 생성
1. 대시보드에서 "New Project" 클릭
2. "Deploy from GitHub repo" 선택
3. GitHub 권한 허용

### 2.3 저장소 선택
1. `metadoor-inspection` 저장소 선택
2. "Deploy" 클릭
3. 배포 시작 (약 2-3분 소요)

### 2.4 배포 상태 확인
1. Deployments 탭에서 진행 상황 확인
2. 초록색 체크마크 = 성공
3. "View Logs"로 실시간 로그 확인

---

## ⚙️ Step 3: 환경 변수 설정

### 3.1 Variables 탭 이동
1. Railway 프로젝트 대시보드
2. "Variables" 탭 클릭

### 3.2 환경 변수 추가
| 변수명 | 값 | 설명 |
|-------|-----|------|
| SECRET_KEY | random-secret-key-123456 | Flask 세션 보안 키 |
| FLASK_ENV | production | 운영 환경 설정 |

### 3.3 배포 재실행
1. "Deployments" 탭
2. 최신 배포 항목의 "Redeploy" 클릭
3. 새 환경 변수로 재배포

---

## 🌐 Step 4: 공용 URL 확인

### 4.1 도메인 확인
1. Railway 프로젝트 대시보드
2. "Settings" 탭
3. "Domains" 섹션에서 자동 생성된 URL 확인
   - 예: `metadoor-inspection.up.railway.app`

### 4.2 커스텀 도메인 설정 (선택)
1. "Domains" 섹션에서 "Add Domain"
2. 소유한 도메인 연결
   - 예: `inspection.yourdomain.com`

### 4.3 URL 테스트
```
https://metadoor-inspection.up.railway.app
```
브라우저에 입력하여 접속 확인

---

## 🔑 Step 5: 접속 및 사용

### 5.1 로그인 정보
**기본 테스트 계정:**
- 아이디: `test`
- 비밀번호: `test`

> ⚠️ **보안 주의**: 운영 환경에서는 데이터베이스를 연결하고 
> 적절한 사용자 관리 시스템을 구축하세요.

### 5.2 점검 앱 사용
1. 위의 URL 접속
2. 아이디/비밀번호 로그인
3. 점검 위치(구) 선택
4. 점검 항목 입력
5. 조치 내용 작성
6. 서명 입력
7. 저장

---

## 🔧 Step 6: 관리 및 모니터링

### 6.1 로그 확인
1. Railway 대시보드
2. "Logs" 탭
3. 실시간 서버 로그 확인

### 6.2 배포 갱신
```bash
git add .
git commit -m "Update: description"
git push origin main
```
→ Railway가 자동으로 감지하여 재배포

### 6.3 비용 확인
1. "Billing" 탭
2. 월 사용량 및 비용 확인
   - 무료: $5/월 크레딧 (충분함)

---

## 🐛 문제 해결

### 배포 실패
```
1. Logs 탭에서 오류 메시지 확인
2. requirements.txt 파일 확인
3. Dockerfile 문법 확인
4. Railway 재배포 시도
```

### 404 오류
```
1. 도메인 URL 다시 확인
2. "Domains" 섹션에서 연결 상태 확인
3. Railway 캐시 갱신 (약 1분)
4. 브라우저 캐시 삭제 (Ctrl+Shift+Delete)
```

### 데이터 저장 안 됨
```
1. "Logs" 탭에서 API 오류 확인
2. 브라우저 개발자 도구 (F12) → Console 확인
3. /api/inspection 엔드포인트 테스트
```

---

## 💡 팁

### 로컬에서 테스트
```bash
pip install -r requirements.txt
python app.py
```
http://localhost:5000 접속

### 자동 배포 끄기
1. "Settings" → "Auto Deploy" → 비활성화
2. 수동 배포: "Redeploy" 버튼

### 로그 다운로드
1. "Logs" 탭
2. 우측 상단 "Download" 버튼

---

## 📚 참고 자료
- Railway 공식 문서: https://docs.railway.app
- Flask 공식 문서: https://flask.palletsprojects.com
- Gunicorn 설정: https://docs.gunicorn.org

---

## ✅ 배포 체크리스트

- [ ] GitHub 저장소 생성 및 코드 업로드
- [ ] Railway 계정 생성
- [ ] GitHub에서 저장소 선택 및 배포
- [ ] 환경 변수 설정 (SECRET_KEY)
- [ ] 배포 성공 확인 (초록색 체크)
- [ ] 공용 URL 확인
- [ ] 브라우저에서 로그인 테스트
- [ ] 점검 데이터 저장 테스트
- [ ] 문서 백업 및 공유

**축하합니다! 메타도어 점검 앱이 클라우드에 배포되었습니다! 🎉**
