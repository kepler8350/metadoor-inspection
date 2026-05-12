# 🚀 메타도어 점검 앱 - Railway 배포 빠른 시작

## 📱 앱 소개
부산 지역 메타도어 유지보수를 위한 **웹 기반 점검 시스템**입니다.
- ✅ 로그인 기능
- ✅ 15개 구(부산) 선택
- ✅ 점검 항목 등록
- ✅ 조치 내용 입력
- ✅ 손글씨 서명 입력
- ✅ 모바일 최적화

---

## ⚡ 5분 배포 가이드

### 1️⃣ 코드 준비 (GitHub)
```bash
# 이 폴더를 GitHub에 업로드
git init
git add .
git commit -m "MetaDoor inspection app"
git push -u origin main
```

### 2️⃣ Railway 배포
1. https://railway.app 접속
2. "New Project" → "Deploy from GitHub"
3. 저장소 선택 → "Deploy"

### 3️⃣ 환경 변수 설정
Railway 대시보드의 "Variables" 탭:
```
SECRET_KEY=your-random-secret-key
```

### 4️⃣ 공용 URL 확인
```
https://metadoor-inspection.up.railway.app
```
(자동 생성되는 도메인)

---

## 🔐 로그인 정보
```
아이디: test
비밀번호: test
```

---

## 📂 프로젝트 구조

```
metadoor-inspection/
├── app.py                    # Flask 백엔드 (핵심 서버)
├── requirements.txt          # Python 패키지 목록
├── Dockerfile                # Docker 설정
├── Procfile                  # Railway 실행 설정
├── package.json              # 프로젝트 정보
│
├── templates/
│   └── index.html            # 화면 구성 (HTML)
│
└── static/
    ├── css/
    │   └── style.css         # 디자인 (스타일)
    └── js/
        └── app.js            # 기능 (자바스크립트)
```

---

## 🎨 화면 구성

### 화면 1: 로그인
- 아이디 입력
- 비밀번호 입력
- 로그인 버튼

### 화면 2: 구 선택
- 금정구, 기장군, 남구, 동구, 동래구
- 부산진구, 북구, 사상구, 사하구, 서구
- 수영구, 연제구, 영도구, 중구, 해운대구

### 화면 3: 점검 항목 입력
- 점검 항목 선택 (도어, 잠금장치, 경첩, 표면, 작동)
- 조치 내용 입력
- 서명 (마우스/터치로 그리기)

### 화면 4: 완료
- 점검 완료 메시지
- 점검 ID 표시

---

## 🔧 커스터마이징

### 구 목록 변경 (app.py)
```python
DISTRICTS = [
    '금정구', '기장군', ...  # 여기 수정
]
```

### 점검 항목 변경 (templates/index.html)
```html
<option value="door_check">도어 점검</option>  <!-- 여기 수정 -->
```

### 디자인 변경 (static/css/style.css)
- 색상: `#1e3c72`, `#2a5298`
- 폰트: 시스템 폰트
- 여백, 크기 등 자유롭게 수정

---

## 📊 기술 스택

| 분야 | 기술 |
|------|------|
| **서버** | Flask (Python) |
| **프론트엔드** | HTML, CSS, JavaScript |
| **배포** | Railway + Docker |
| **데이터** | 세션 저장소 (메모리) |

---

## 🚢 배포 플랫폼: Railway

### Railway란?
- Cloud 호스팅 서비스
- GitHub 연동으로 자동 배포
- 월 $5 크레딧 무료 제공
- 간단하고 빠른 배포

### Railway 주요 기능
- ✅ 자동 재배포
- ✅ 환경 변수 관리
- ✅ 실시간 로그 확인
- ✅ 모니터링 대시보드
- ✅ 커스텀 도메인 연결

---

## 💾 데이터 저장 (현재)

현재는 **메모리에만 저장**되므로:
- 서버 재시작 시 데이터 삭제
- 여러 명이 사용 불가

**운영을 위해서는 데이터베이스 추가 필요:**
```python
# 추후 추가 가능:
- PostgreSQL
- MongoDB
- Firebase
```

---

## 🐛 문제 해결

### 404 Not Found
```
✓ 도메인 URL 다시 확인
✓ Railway 배포 완료 확인
✓ 브라우저 캐시 삭제
```

### 로그인 실패
```
✓ 아이디: test, 비밀번호: test 입력
✓ 대소문자 구분 주의
```

### 데이터 저장 안 됨
```
✓ 브라우저 개발자 도구 (F12) 열기
✓ Console 탭에서 오류 메시지 확인
✓ Railway Logs 탭 확인
```

---

## 📞 지원

### Railway 문제
- 공식 문서: https://docs.railway.app
- 상태 페이지: https://status.railway.app

### Flask 문제
- 공식 문서: https://flask.palletsprojects.com
- 튜토리얼: https://flask.palletsprojects.com/tutorial/

---

## 📝 다음 단계

1. ✅ 이 코드를 GitHub에 업로드
2. ✅ Railway에 배포
3. ⬜ 사용자 계정 관리 추가
4. ⬜ 데이터베이스 연동
5. ⬜ 점검 결과 리포팅 기능
6. ⬜ 오프라인 모드 추가
7. ⬜ 모바일 앱으로 발전

---

## 📄 라이선스
MIT License - 자유롭게 사용, 수정, 배포 가능

---

## 🎉 축하합니다!

메타도어 점검 앱이 준비되었습니다.
Railway를 통해 전 세계 어디서든 접속할 수 있습니다! 🌍

**시작하기:**
1. GitHub에 업로드
2. Railway 배포
3. 공용 URL 공유
4. 사용 시작

**질문이 있으신가요?**
- README.md 확인
- DEPLOYMENT_GUIDE_KO.md 참고
- Railway 공식 문서 방문
