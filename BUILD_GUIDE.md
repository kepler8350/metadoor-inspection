# 📱 메타도어 모바일 앱 빌드 및 배포 가이드

## 🎯 목표

React Native + Expo를 사용해 **iOS/Android 네이티브 모바일 앱** 빌드 및 배포

## 📋 전제 조건

### 필수 설치 항목

1. **Node.js** (v14 이상)
   ```bash
   # 버전 확인
   node --version
   npm --version
   ```

2. **Expo CLI** (글로벌 설치)
   ```bash
   npm install -g expo-cli
   ```

3. **EAS CLI** (배포용)
   ```bash
   npm install -g eas-cli
   ```

4. **Android Studio** (Android 빌드용)
   - Android SDK
   - Android Emulator

5. **Xcode** (iOS 빌드용, Mac만 해당)
   - iOS SDK
   - iOS Simulator

## 🚀 빌드 과정

### 1️⃣ 로컬 개발 환경에서 테스트

```bash
# 프로젝트 디렉토리로 이동
cd metadoor-inspection-app

# 의존성 설치
npm install

# Expo 개발 서버 시작
expo start

# 선택지
# a - Android Emulator에서 실행
# i - iOS Simulator에서 실행 (Mac)
# w - 웹 브라우저에서 실행 (테스트용)
# j - Metro 번들러 열기
# r - 서버 재시작
```

### 2️⃣ EAS 빌드 계정 설정

```bash
# EAS 계정 로그인
eas login

# 또는 회원가입
eas register
```

### 3️⃣ 프로젝트 초기화

```bash
# EAS 프로젝트 생성/연결
eas init

# 또는 기존 프로젝트 연결
eas init --id=metadoor-inspection
```

### 4️⃣ Android APK 빌드

#### 방법 A: EAS Build (클라우드)

```bash
# Android APK 빌드
eas build --platform android --type apk

# 빌드 완료 후 다운로드
# 대략 5-15분 소요
```

#### 방법 B: 로컬 빌드 (Advanced)

```bash
# 필수: Android Studio 설치 필수

# 로컬 빌드
eas build --platform android --type apk --local
```

### 5️⃣ iOS IPA 빌드 (Mac 필수)

```bash
# iOS IPA 빌드
eas build --platform ios

# 또는 APK 형식
eas build --platform ios --type ipa

# 빌드 완료 후 다운로드
# 대략 10-20분 소요
```

### 6️⃣ Android에 APK 배포

```bash
# 1. APK 다운로드
# EAS 빌드 완료 후 다운로드 링크에서 APK 파일 다운로드

# 2. 디바이스에 설치
# 방법 1: USB 케이블 연결
adb install metadoor-inspection-app.apk

# 방법 2: 직접 다운로드
# APK 파일을 이메일/클라우드로 전송
# 디바이스에서 직접 설치

# 방법 3: Google Play Store
# (별도의 계정 및 설정 필요)
```

### 7️⃣ iOS에 IPA 배포

```bash
# 1. IPA 다운로드
# EAS 빌드 완료 후 다운로드

# 2. Testflight (권장)
# Apple Developer 계정 필요
# https://testflight.apple.com에 업로드

# 3. 디바이스에 직접 설치 (개발용)
# Xcode를 사용하여 설치
xcode-select --install
open -a Xcode metadoor-inspection-app.ipa
```

## 📱 앱 스토어 배포

### Google Play Store

1. **Google Developer 계정 생성** ($25)
   - https://play.google.com/console

2. **앱 정보 작성**
   - 앱 이름
   - 설명
   - 스크린샷
   - 아이콘

3. **빌드 업로드**
   ```bash
   # Signed APK 생성
   eas build --platform android --type aab
   ```

4. **배포**
   - Google Play Console에 업로드
   - 검수 대기 (보통 몇 시간 ~ 며칠)

### Apple App Store

1. **Apple Developer 계정** ($99/년)
   - https://developer.apple.com

2. **프로바이저닝 프로필 설정**
   ```bash
   # iOS 인증서/프로필 설정
   eas credentials
   ```

3. **빌드 업로드**
   ```bash
   # Testflight 빌드
   eas build --platform ios
   ```

4. **App Store Connect에서 배포**
   - https://appstoreconnect.apple.com
   - 앱 정보 입력
   - 배포 대기 (보통 1-3일)

## 🔧 트러블슈팅

### 빌드 실패

```bash
# 1. 캐시 삭제
rm -rf node_modules
rm package-lock.json
npm install

# 2. Expo 캐시 삭제
expo start --clear

# 3. EAS 빌드 로그 확인
eas build --status
```

### 앱 실행 오류

```bash
# Metro 번들러 재시작
npm start -- --reset-cache

# 또는
expo start -c
```

### 권한 오류

```bash
# Android 권한 확인
# AndroidManifest.xml 수정 필요

# iOS 권한 확인
# Info.plist에 권한 추가 필요
```

## 📊 모니터링 및 업데이트

### 앱 업데이트

```bash
# 버전 업데이트
# package.json에서 version 수정

# app.json에서 expo.version 수정

# 새로운 빌드 생성
eas build --platform android
eas build --platform ios
```

### 심볼 저장 (디버깅용)

```bash
# 심볼 업로드 (Sentry 등과 통합)
eas build:list
eas build:view <BUILD_ID>
```

## 📈 성능 최적화

```bash
# 번들 크기 분석
npm run analyze

# 프로덕션 빌드
eas build --platform android --type apk --release
```

## 🔒 보안 설정

### 코드 서명

```bash
# 자동 서명 (권장)
eas build --platform android --type apk

# 또는 수동 서명
eas credentials
```

### 환경 변수

```bash
# .env 파일 생성 (절대 커밋하지 마세요!)
REACT_APP_API_URL=https://api.metadoor.com
REACT_APP_VERSION=1.0.0
```

## 📚 참고 자료

- [Expo 공식 문서](https://docs.expo.dev)
- [React Native 공식 문서](https://reactnative.dev)
- [EAS 빌드 문서](https://docs.expo.dev/eas-update/introduction/)
- [Google Play Store 배포](https://play.google.com/console/about/guides/releasewithconfidence/)
- [Apple App Store 배포](https://developer.apple.com/app-store/review/guidelines/)

---

**질문이나 문제가 있으면 GitHub Issues에 보고해주세요!**
