# 메타도어 점검 앱 - Railway 배포 가이드

## 📋 프로젝트 소개
메타도어 유지보수를 위한 점검 모바일 웹 앱입니다. Railway 웹서비스를 통해 공용 URL로 접속하여 사용할 수 있습니다.

## 🚀 배포 방법

### 1단계: GitHub 준비
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/your-username/metadoor-inspection.git
git push -u origin main
```

### 2단계: Railway 배포
1. https://railway.app 접속
2. GitHub 계정으로 로그인
3. "New Project" 클릭
4. "Deploy from GitHub repo" 선택
5. 저장소 선택 및 배포

### 3단계: 환경 변수 설정
Railway 대시보드에서:
- `SECRET_KEY` = (무작위 보안 키 입력)
- `PORT` = 8000 (자동 설정)

## 📱 사용 방법

### 로그인
- 아이디: test (또는 관리자가 등록한 아이디)
- 비밀번호: test (또는 관리자가 지정한 비밀번호)

### 점검 절차
1. 로그인
2. 구 선택 (금정구, 기장군 등)
3. 점검 항목 선택
4. 조치 내용 입력
5. 서명 (마우스 또는 터치)
6. 저장

## 🔧 로컬 테스트

### 설치
```bash
pip install -r requirements.txt
```

### 실행
```bash
python app.py
```

브라우저에서 `http://localhost:5000` 접속

## 📦 파일 구조
```
metadoor-inspection/
├── app.py                 # Flask 백엔드
├── requirements.txt       # Python 의존성
├── Dockerfile            # Docker 설정
├── Procfile              # 배포 설정
├── templates/
│   └── index.html        # HTML 템플릿
└── static/
    ├── css/
    │   └── style.css     # 스타일시트
    └── js/
        └── app.js        # 자바스크립트
```

## ✨ 기능

- ✅ 사용자 인증
- ✅ 구 선택
- ✅ 점검 항목 선택
- ✅ 조치 내용 입력
- ✅ 서명 입력 (마우스/터치)
- ✅ 점검 데이터 저장
- ✅ 모바일 반응형 디자인

## 🔐 보안

- Flask 세션 기반 인증
- HTTPS 지원 (Railway에서 자동)
- SECRET_KEY 환경 변수로 관리

## 📞 지원

문제 발생 시:
1. Railway 로그 확인
2. 브라우저 콘솔 오류 확인
3. Flask 서버 재시작

## 🎨 커스터마이징

### 구 목록 수정 (app.py)
```python
DISTRICTS = [
    '금정구', '기장군', ...
]
```

### 점검 항목 수정 (templates/index.html)
```html
<option value="custom_item">항목명</option>
```

### 스타일 변경 (static/css/style.css)
색상, 폰트, 레이아웃 등 자유롭게 수정 가능

## 📄 라이선스
MIT License
