# 📱 메타도어 모바일 앱 - 최종 가이드

## 🎉 축하합니다!

**메타도어 모바일 점검 앱**이 완성되었습니다!

✅ React Native + Expo  
✅ iOS & Android 지원  
✅ 전문적인 모바일 UI/UX 디자인  
✅ 로그인, 대시보드, 점검 입력, 설정 기능 완성  

---

## 🚀 5분 안에 시작하기

### 1️⃣ 필수 도구 설치

```bash
# Node.js 설치 (이미 설치하셨으면 스킵)
# https://nodejs.org/en/download/

# Expo CLI 글로벌 설치
npm install -g expo-cli

# 프로젝트 디렉토리로 이동
cd metadoor-inspection-app
```

### 2️⃣ 의존성 설치

```bash
npm install
```

### 3️⃣ 앱 실행

```bash
npm start
# 또는
expo start
```

### 4️⃣ 디바이스에서 보기

**Option A: 휴대폰에서 직접 보기 (가장 쉬움)**

1. **Expo Go 앱 설치**
   - iOS: App Store에서 "Expo Go" 검색
   - Android: Google Play Store에서 "Expo Go" 검색

2. **QR 코드 스캔**
   - 터미널에 나타난 QR 코드를 스캔하면 바로 앱이 실행됩니다!

**Option B: 에뮬레이터에서 보기**

```bash
# Android Emulator
npm run android
# 또는 'a' 키 누르기

# iOS Simulator (Mac만 가능)
npm run ios
# 또는 'i' 키 누르기
```

**Option C: 웹 브라우저에서 테스트**

```bash
npm run web
# 또는 'w' 키 누르기
```

---

## 🎨 앱 화면 구성

### 📱 로그인 화면
- **디자인**: 파란 그래디언트 배경 + 화이트 카드
- **기능**: 아이디/비밀번호 입력
- **테스트 계정**: `admin` / `admin123`

### 🏠 대시보드
- **통계**: 총 점검 횟수, 이달 점검 수
- **액션 버튼**: 새 점검 입력, 점검 이력
- **최근 활동**: 점검 기록 타임라인

### ✏️ 점검 입력
- **위치 선택**: 부산 15개 구를 그리드로 표시
- **항목 선택**: 외벽, 지붕, 창호, 바닥, 내벽, 기타
- **조사 내용**: 텍스트 입력
- **사진**: 갤러리/카메라에서 업로드
- **점검 상태**: 정상, 요주의, 이상 (버튼식)
- **완료**: 임시저장 또는 완료

### ⚙️ 설정
- **계정**: 사용자명, 역할
- **알림**: 푸시 알림 설정
- **화면**: 다크 모드 설정
- **정보**: 버전, 빌드 번호, 업데이트
- **로그아웃**: 계정 로그아웃

---

## 📁 프로젝트 구조

```
metadoor-inspection-app/
├── App.tsx                           # 메인 앱 진입점
├── app.json                          # Expo 설정
├── package.json                      # npm 의존성
├── MOBILE_APP_README.md              # 앱 설명서
├── BUILD_GUIDE.md                    # 빌드 & 배포 가이드
└── screens/                          # 화면 컴포넌트
    ├── LoginScreen.tsx               # 로그인 (프로페셔널 디자인)
    ├── DashboardScreen.tsx           # 대시보드 (통계 + 액션)
    ├── InspectionListScreen.tsx      # 위치 선택 (그리드 UI)
    ├── InspectionDetailScreen.tsx    # 점검 입력 (완전한 폼)
    └── SettingsScreen.tsx            # 설정 (계정 & 정보)
```

---

## 🎨 디자인 특징

### 색상
- **Primary Blue**: `#1e5a96` (로고, 헤더, 액션)
- **Dark Blue**: `#164a7a` (진한 강조)
- **Background**: `#f5f7fa` (밝은 배경)
- **White**: `#ffffff` (카드)

### 폰트
- **제목**: 28px, 700 bold, -0.5 letterSpacing
- **서브제목**: 14px, 400 normal
- **라벨**: 13px, 700 bold
- **본문**: 14-15px, 400-500 normal

### 컴포넌트
- **카드**: borderRadius: 14, 부드러운 그림자
- **버튼**: borderRadius: 12, 터치 시 스케일 변화
- **입력**: borderRadius: 10, 밝은 배경
- **네비게이션**: 하단 탭 바, 아이콘 + 라벨

---

## 🔧 기술 스택

| 분류 | 기술 |
|------|------|
| **Framework** | React Native |
| **Build Tool** | Expo |
| **Navigation** | React Navigation (Bottom Tabs + Stack) |
| **Image Picker** | expo-image-picker |
| **Status Bar** | expo-status-bar |
| **Language** | TypeScript |
| **State** | React Hooks (useState) |

---

## 📦 빌드 및 배포

### Android APK 빌드

```bash
# EAS 빌드 (클라우드)
eas build --platform android --type apk

# 또는 로컬 빌드
eas build --platform android --type apk --local
```

### iOS 빌드

```bash
# Mac에서만 가능
eas build --platform ios
```

### Play Store 배포

1. Google Play Console 계정 생성 ($25)
2. 앱 정보 입력 (이름, 설명, 스크린샷)
3. 서명된 AAB 빌드 생성
4. 업로드 후 검수 대기

### App Store 배포

1. Apple Developer 계정 ($99/년)
2. 인증서/프로필 설정
3. IPA 빌드 생성
4. App Store Connect에 업로드

---

## 📞 지원

- **GitHub**: https://github.com/kepler8350/metadoor-inspection
- **문서**: MOBILE_APP_README.md, BUILD_GUIDE.md 참조

---

## ✨ 완성된 기능

- ✅ React Native + Expo 설정
- ✅ 5개 화면 (로그인, 대시보드, 위치선택, 점검입력, 설정)
- ✅ 프로페셔널 모바일 UI/UX 디자인
- ✅ 이미지 업로드 (카메라/갤러리)
- ✅ 하단 탭 네비게이션
- ✅ StatusBar 및 SafeAreaView
- ✅ 터치 피드백 (activeOpacity)
- ✅ iOS & Android 호환성

---

## 🎊 시작하기

```bash
npm start
# QR 코드 스캔하거나 에뮬레이터 실행
# 테스트 계정: admin / admin123
```

**Happy coding!** 🚀
