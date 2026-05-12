# 메타도어 모바일 점검 앱

![메타도어](./assets/icon.png)

**유지보수 점검 시스템** - React Native + Expo로 만든 모바일 앱

## 📱 앱 기능

### ✅ 구현된 기능

- **로그인** - 아이디/비밀번호 인증
- **대시보드** - 점검 통계, 액션 버튼
- **점검 입력**
  - 점검 위치(부산 15개 구) 선택
  - 점검 항목 선택 (외벽, 지붕, 창호, 바닥, 내벽, 기타)
  - 조사 내용 입력
  - 사진 촬영/갤러리 업로드
  - 점검 상태 선택 (정상, 요주의, 이상)
- **설정** - 계정정보, 알림설정, 앱 정보

## 🚀 설치 및 실행

### 필수 요구사항

- **Node.js** v14 이상
- **npm** 또는 **yarn**
- **Expo CLI** (선택사항)
- **Android/iOS 디바이스** 또는 에뮬레이터

### 설치 방법

#### 1️⃣ 프로젝트 디렉토리로 이동

```bash
cd metadoor-inspection-app
```

#### 2️⃣ 의존성 설치

```bash
npm install
# 또는
yarn install
```

#### 3️⃣ Expo 시작

```bash
npm start
# 또는
expo start
```

#### 4️⃣ 앱 실행

**Android:**
```bash
npm run android
# 또는 'a' 키 누르기
```

**iOS:**
```bash
npm run ios
# 또는 'i' 키 누르기
```

**웹 (테스트용):**
```bash
npm run web
# 또는 'w' 키 누르기
```

## 📁 프로젝트 구조

```
metadoor-inspection-app/
├── App.tsx                          # 메인 진입점
├── app.json                         # Expo 설정
├── package.json                     # 의존성
├── screens/
│   ├── LoginScreen.tsx              # 로그인 화면
│   ├── DashboardScreen.tsx          # 대시보드
│   ├── InspectionListScreen.tsx     # 점검 위치 선택
│   ├── InspectionDetailScreen.tsx   # 점검 입력 폼
│   └── SettingsScreen.tsx           # 설정
├── assets/
│   ├── icon.png                     # 앱 아이콘
│   ├── splash.png                   # 스플래시 화면
│   └── adaptive-icon.png            # Android 아이콘
└── README.md                        # 이 파일
```

## 🔑 테스트 계정

```
ID: admin
Password: admin123
```

## 🎨 주요 색상

- **Primary Blue**: #1e5a96
- **Dark Blue**: #164a7a
- **Background**: #f5f5f5
- **White**: #fff

## 📱 화면 구성

### 1. 로그인 화면
- 파란 배경(그래디언트)
- 화이트 카드 레이아웃
- 아이디/비밀번호 입력

### 2. 대시보드
- 점검 통계 (총 횟수, 이달 점검)
- 새 점검 입력 버튼
- 점검 이력 보기 버튼

### 3. 점검 입력
- 부산 15개 구 선택
- 점검 항목 드롭다운
- 조사 내용 텍스트 입력
- 사진 촬영/갤러리 업로드
- 점검 상태 선택
- 저장/완료 버튼

### 4. 설정
- 계정 정보 표시
- 알림 설정 토글
- 다크 모드 (미구현)
- 로그아웃 버튼

## 🛠️ 기술 스택

- **Framework**: React Native
- **Build Tool**: Expo
- **Navigation**: React Navigation (Bottom Tabs + Stack)
- **Image Picker**: expo-image-picker
- **Language**: TypeScript
- **State Management**: React Hooks

## 📦 빌드 및 배포

### APK 빌드 (Android)

```bash
eas build --platform android
```

### IPA 빌드 (iOS)

```bash
eas build --platform ios
```

### 웹 배포

```bash
npm run web
# 또는 Vercel/Netlify에 배포
```

## 🔐 보안

- ✅ 로그인 인증
- ✅ 세션 관리
- ⚠️ 실제 프로덕션에서는 추가 보안 조치 필요
  - JWT 토큰 기반 인증
  - HTTPS 통신
  - 데이터 암호화

## 📞 라이선스

MIT License

## 👤 개발자

메타도어 점검 앱 팀

---

**문의사항이 있으시면 admin@metadoor.com으로 연락주세요.**
