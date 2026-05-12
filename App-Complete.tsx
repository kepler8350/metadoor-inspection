import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  Image,
  SafeAreaView,
  StatusBar,
  StyleSheet,
  Dimensions,
  Alert,
  KeyboardAvoidingView,
  Platform,
  Switch,
  FlatList,
} from 'react-native';

const { width, height } = Dimensions.get('window');

// 색상 팔레트
const Colors = {
  primary: '#1e5a96',
  dark: '#164a7a',
  light: '#f5f7fa',
  white: '#ffffff',
  gray: '#999999',
  lightGray: '#e0e0e0',
  danger: '#ff6b6b',
  success: '#4caf50',
};

// ========================
// 로그인 화면
// ========================
const LoginScreen = ({ onLogin }) => {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = () => {
    if (!username || !password) {
      Alert.alert('입력 오류', '아이디와 비밀번호를 입력하세요.');
      return;
    }
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      if (username === 'admin' && password === 'admin123') {
        onLogin();
      } else {
        Alert.alert('로그인 실패', '아이디 또는 비밀번호가 올바르지 않습니다.');
      }
    }, 500);
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor={Colors.primary} />
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={{ flex: 1 }}
      >
        <View style={styles.backgroundGradient}>
          <View style={{ flex: 0.3 }} />
          <View style={styles.loginCard}>
            <View style={styles.logoSection}>
              <Text style={styles.logoEmoji}>🏛️</Text>
              <Text style={styles.appTitle}>메타도어</Text>
              <Text style={styles.appSubtitle}>유지보수 점검 시스템</Text>
            </View>

            <View style={styles.formGroup}>
              <Text style={styles.formLabel}>아이디</Text>
              <TextInput
                style={styles.input}
                placeholder="아이디"
                placeholderTextColor="#bbb"
                value={username}
                onChangeText={setUsername}
                editable={!isLoading}
              />
            </View>

            <View style={styles.formGroup}>
              <Text style={styles.formLabel}>비밀번호</Text>
              <TextInput
                style={styles.input}
                placeholder="비밀번호"
                placeholderTextColor="#bbb"
                value={password}
                onChangeText={setPassword}
                secureTextEntry
                editable={!isLoading}
              />
            </View>

            <TouchableOpacity
              style={[styles.primaryButton, isLoading && { opacity: 0.7 }]}
              onPress={handleLogin}
              disabled={isLoading}
            >
              <Text style={styles.buttonText}>
                {isLoading ? '로그인 중...' : '로그인'}
              </Text>
            </TouchableOpacity>

            <Text style={styles.helpText}>
              권한자가 등록한 직원만{'\n'}로그인할 수 있습니다.
            </Text>
          </View>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

// ========================
// 대시보드 화면
// ========================
const DashboardScreen = ({ onNavigateToInspection }) => {
  const [stats] = useState({
    totalInspections: 12,
    thisMonthInspections: 5,
  });

  const [activities] = useState([
    { time: '오늘 14:30', desc: '사상구 - 외벽 점검 완료' },
    { time: '어제 10:15', desc: '부산진구 - 지붕 점검 완료' },
    { time: '3일 전', desc: '남구 - 창호 점검 완료' },
  ]);

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor={Colors.primary} />
      <ScrollView style={{ flex: 1 }} showsVerticalScrollIndicator={false}>
        {/* 헤더 */}
        <View style={styles.header}>
          <View>
            <Text style={styles.headerTitle}>대시보드</Text>
            <Text style={styles.headerSubtitle}>admin님 환영합니다!</Text>
          </View>
          <View style={styles.userButton}>
            <Text style={{ fontSize: 24 }}>👤</Text>
          </View>
        </View>

        <View style={styles.content}>
          {/* 통계 카드 */}
          <View style={styles.statsGrid}>
            <View style={styles.statCard}>
              <Text style={styles.statValue}>{stats.totalInspections}</Text>
              <Text style={styles.statLabel}>총 점검 횟수</Text>
              <View style={styles.statBadge}>
                <Text style={{ fontSize: 20 }}>📊</Text>
              </View>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statValue}>{stats.thisMonthInspections}</Text>
              <Text style={styles.statLabel}>이달 점검</Text>
              <View style={styles.statBadge}>
                <Text style={{ fontSize: 20 }}>📅</Text>
              </View>
            </View>
          </View>

          {/* 액션 버튼 */}
          <TouchableOpacity
            style={[styles.actionCard, { backgroundColor: Colors.primary }]}
            onPress={onNavigateToInspection}
          >
            <Text style={{ fontSize: 24, marginRight: 12 }}>✏️</Text>
            <View style={{ flex: 1 }}>
              <Text style={styles.actionTitle}>새 점검 입력</Text>
              <Text style={[styles.actionSubtitle, { color: 'rgba(255,255,255,0.7)' }]}>
                오늘의 점검을 시작하세요
              </Text>
            </View>
            <Text style={{ fontSize: 20, color: 'rgba(255,255,255,0.5)' }}>›</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.actionCard}>
            <Text style={{ fontSize: 24, marginRight: 12 }}>📋</Text>
            <View style={{ flex: 1 }}>
              <Text style={styles.actionTitle}>점검 이력</Text>
              <Text style={styles.actionSubtitle}>지난 점검 기록 보기</Text>
            </View>
            <Text style={{ fontSize: 20, color: Colors.lightGray }}>›</Text>
          </TouchableOpacity>

          {/* 최근 활동 */}
          <Text style={styles.sectionTitle}>최근 활동</Text>
          <View style={styles.activityCard}>
            {activities.map((activity, idx) => (
              <View key={idx}>
                <View style={styles.activityItem}>
                  <View style={styles.activityDot} />
                  <View style={{ flex: 1 }}>
                    <Text style={styles.activityTime}>{activity.time}</Text>
                    <Text style={styles.activityDesc}>{activity.desc}</Text>
                  </View>
                </View>
                {idx < activities.length - 1 && (
                  <View style={{ height: 1, backgroundColor: '#f0f0f0', marginVertical: 12 }} />
                )}
              </View>
            ))}
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

// ========================
// 점검 위치 선택 화면
// ========================
const InspectionListScreen = ({ onSelectDistrict }) => {
  const [selectedDistrict, setSelectedDistrict] = useState(null);

  const districts = [
    '금정구', '기장군', '남구', '동구', '동래구',
    '부산진구', '북구', '사상구', '사하구', '서구',
    '수영구', '연제구', '영도구', '중구', '해운대구',
  ];

  const handleSelect = (district) => {
    setSelectedDistrict(district);
    setTimeout(() => onSelectDistrict(district), 200);
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor={Colors.primary} />
      <View style={styles.header}>
        <Text style={styles.headerTitle}>점검 위치 선택</Text>
        <Text style={styles.headerSubtitle}>2단계 / 3단계</Text>
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        <View style={styles.guideBox}>
          <Text style={{ fontSize: 20 }}>📍</Text>
          <Text style={styles.guideText}>점검할 지역을 선택하세요</Text>
        </View>

        <View style={styles.districtGrid}>
          {districts.map((district) => (
            <TouchableOpacity
              key={district}
              style={[
                styles.districtCard,
                selectedDistrict === district && styles.districtCardSelected,
              ]}
              onPress={() => handleSelect(district)}
            >
              <Text style={styles.districtName}>{district}</Text>
            </TouchableOpacity>
          ))}
        </View>
        <View style={{ height: 20 }} />
      </ScrollView>
    </SafeAreaView>
  );
};

// ========================
// 점검 입력 화면
// ========================
const InspectionDetailScreen = ({ district, onComplete, onBack }) => {
  const [inspectionType, setInspectionType] = useState('');
  const [content, setContent] = useState('');
  const [status, setStatus] = useState('정상');

  const inspectionTypes = ['외벽', '지붕', '창호', '바닥', '내벽', '기타'];

  const handleSubmit = () => {
    if (!inspectionType) {
      Alert.alert('입력 오류', '점검 항목을 선택하세요.');
      return;
    }
    Alert.alert('✓ 완료', '점검이 저장되었습니다.', [
      { text: '확인', onPress: onComplete },
    ]);
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor={Colors.primary} />
      <View style={styles.header}>
        <TouchableOpacity
          onPress={onBack}
          style={{ width: 40, height: 40, justifyContent: 'center' }}
        >
          <Text style={{ fontSize: 28, color: Colors.white }}>‹</Text>
        </TouchableOpacity>
        <View>
          <Text style={styles.headerTitle}>점검 입력</Text>
          <Text style={styles.headerSubtitle}>{district} - 점검 입력 / 3단계</Text>
        </View>
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        <View style={styles.progressBar}>
          <View style={[styles.progressFill, { width: '66%' }]} />
        </View>

        {/* 점검 항목 */}
        <View style={styles.section}>
          <Text style={styles.sectionLabel}>점검 항목</Text>
          <View style={styles.typeGrid}>
            {inspectionTypes.map((type) => (
              <TouchableOpacity
                key={type}
                style={[
                  styles.typeButton,
                  inspectionType === type && styles.typeButtonActive,
                ]}
                onPress={() => setInspectionType(type)}
              >
                <Text
                  style={[
                    styles.typeButtonText,
                    inspectionType === type && styles.typeButtonTextActive,
                  ]}
                >
                  {type}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* 조사 내용 */}
        <View style={styles.section}>
          <Text style={styles.sectionLabel}>조사 내용</Text>
          <Text style={styles.sectionDescription}>
            이상 발견 시 조사 내용을 기록하세요
          </Text>
          <TextInput
            style={styles.textArea}
            placeholder="예: 페널 박인 → 조기화 완료"
            placeholderTextColor="#bbb"
            multiline
            numberOfLines={4}
            value={content}
            onChangeText={setContent}
          />
        </View>

        {/* 사진 */}
        <View style={styles.section}>
          <Text style={styles.sectionLabel}>사진</Text>
          <View style={styles.imageUpload}>
            <Text style={{ fontSize: 36, marginBottom: 8 }}>📷</Text>
            <Text style={styles.imageUploadText}>사진 추가</Text>
          </View>
        </View>

        {/* 점검 상태 */}
        <View style={styles.section}>
          <Text style={styles.sectionLabel}>점검 상태</Text>
          <View style={styles.statusGrid}>
            {['정상', '요주의', '이상'].map((s) => (
              <TouchableOpacity
                key={s}
                style={[
                  styles.statusButton,
                  status === s && styles.statusButtonActive,
                ]}
                onPress={() => setStatus(s)}
              >
                <Text
                  style={[
                    styles.statusButtonText,
                    status === s && styles.statusButtonTextActive,
                  ]}
                >
                  {s}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* 버튼 */}
        <View style={styles.buttonGroup}>
          <TouchableOpacity style={[styles.primaryButton, { flex: 1 }]}>
            <Text style={styles.buttonText}>임시 저장</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.primaryButton, { flex: 1, backgroundColor: Colors.primary }]}
            onPress={handleSubmit}
          >
            <Text style={styles.buttonText}>완료</Text>
          </TouchableOpacity>
        </View>

        <View style={{ height: 20 }} />
      </ScrollView>
    </SafeAreaView>
  );
};

// ========================
// 설정 화면
// ========================
const SettingsScreen = ({ onLogout }) => {
  const [notifications, setNotifications] = useState(true);
  const [darkMode, setDarkMode] = useState(false);

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor={Colors.primary} />
      <View style={styles.header}>
        <View>
          <Text style={styles.headerTitle}>설정</Text>
          <Text style={styles.headerSubtitle}>앱 설정 및 정보</Text>
        </View>
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* 계정 */}
        <Text style={styles.sectionTitle}>계정</Text>
        <View style={styles.settingCard}>
          <View style={styles.settingItem}>
            <View>
              <Text style={styles.settingLabel}>사용자명</Text>
              <Text style={styles.settingValue}>admin</Text>
            </View>
            <Text style={{ fontSize: 20 }}>👤</Text>
          </View>
          <View style={[styles.settingItem, { borderTopWidth: 1, borderTopColor: '#f0f0f0', marginTop: 12, paddingTop: 12 }]}>
            <View>
              <Text style={styles.settingLabel}>역할</Text>
              <Text style={styles.settingValue}>관리자</Text>
            </View>
            <Text style={{ fontSize: 20 }}>👨‍💼</Text>
          </View>
        </View>

        {/* 알림 */}
        <Text style={styles.sectionTitle}>알림</Text>
        <View style={styles.settingCard}>
          <View style={styles.settingItem}>
            <View>
              <Text style={styles.settingLabel}>푸시 알림</Text>
              <Text style={styles.settingDescription}>점검 완료 시 알림</Text>
            </View>
            <Switch
              value={notifications}
              onValueChange={setNotifications}
              trackColor={{ false: '#ddd', true: Colors.success }}
              thumbColor={notifications ? Colors.primary : '#999'}
            />
          </View>
        </View>

        {/* 화면 */}
        <Text style={styles.sectionTitle}>화면</Text>
        <View style={styles.settingCard}>
          <View style={styles.settingItem}>
            <View>
              <Text style={styles.settingLabel}>다크 모드</Text>
              <Text style={styles.settingDescription}>야간 모드</Text>
            </View>
            <Switch
              value={darkMode}
              onValueChange={setDarkMode}
              trackColor={{ false: '#ddd', true: Colors.success }}
              thumbColor={darkMode ? Colors.primary : '#999'}
            />
          </View>
        </View>

        {/* 정보 */}
        <Text style={styles.sectionTitle}>정보</Text>
        <View style={styles.settingCard}>
          <View style={styles.settingItem}>
            <Text style={styles.settingLabel}>앱 버전</Text>
            <Text style={styles.settingValue}>1.0.0</Text>
          </View>
        </View>

        {/* 로그아웃 */}
        <TouchableOpacity
          style={styles.logoutButton}
          onPress={() => {
            Alert.alert('로그아웃', '정말 로그아웃 하시겠습니까?', [
              { text: '취소' },
              { text: '로그아웃', onPress: onLogout, style: 'destructive' },
            ]);
          }}
        >
          <Text style={styles.logoutButtonText}>로그아웃</Text>
        </TouchableOpacity>

        <View style={{ height: 20 }} />
      </ScrollView>
    </SafeAreaView>
  );
};

// ========================
// 메인 앱 컴포넌트
// ========================
export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentScreen, setCurrentScreen] = useState('dashboard');
  const [selectedDistrict, setSelectedDistrict] = useState(null);

  if (!isLoggedIn) {
    return <LoginScreen onLogin={() => setIsLoggedIn(true)} />;
  }

  switch (currentScreen) {
    case 'dashboard':
      return (
        <DashboardScreen
          onNavigateToInspection={() => setCurrentScreen('inspectionList')}
        />
      );
    case 'inspectionList':
      return (
        <InspectionListScreen
          onSelectDistrict={(district) => {
            setSelectedDistrict(district);
            setCurrentScreen('inspectionDetail');
          }}
        />
      );
    case 'inspectionDetail':
      return (
        <InspectionDetailScreen
          district={selectedDistrict}
          onComplete={() => setCurrentScreen('dashboard')}
          onBack={() => setCurrentScreen('inspectionList')}
        />
      );
    case 'settings':
      return (
        <SettingsScreen
          onLogout={() => {
            setIsLoggedIn(false);
            setCurrentScreen('dashboard');
          }}
        />
      );
    default:
      return <DashboardScreen />;
  }
}

// ========================
// 스타일시트
// ========================
const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.light,
  },
  backgroundGradient: {
    flex: 1,
    backgroundColor: Colors.primary,
    justifyContent: 'center',
    paddingHorizontal: 20,
  },
  header: {
    backgroundColor: Colors.primary,
    paddingHorizontal: 20,
    paddingVertical: 16,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: '700',
    color: Colors.white,
    marginBottom: 4,
    letterSpacing: -0.5,
  },
  headerSubtitle: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.7)',
  },
  userButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  loginCard: {
    backgroundColor: Colors.white,
    borderRadius: 20,
    paddingVertical: 40,
    paddingHorizontal: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.25,
    shadowRadius: 20,
    elevation: 10,
  },
  logoSection: {
    alignItems: 'center',
    marginBottom: 30,
  },
  logoEmoji: {
    fontSize: 56,
    marginBottom: 12,
  },
  appTitle: {
    fontSize: 32,
    fontWeight: '700',
    color: '#333',
    marginBottom: 6,
    letterSpacing: -0.5,
  },
  appSubtitle: {
    fontSize: 14,
    color: Colors.gray,
    fontWeight: '400',
  },
  content: {
    flex: 1,
    paddingHorizontal: 16,
    paddingVertical: 16,
  },
  formGroup: {
    marginBottom: 20,
    gap: 8,
  },
  formLabel: {
    fontSize: 13,
    fontWeight: '600',
    color: '#333',
    letterSpacing: 0.3,
  },
  input: {
    paddingHorizontal: 14,
    paddingVertical: 12,
    fontSize: 15,
    color: '#333',
    backgroundColor: '#f8f8f8',
    borderRadius: 10,
  },
  primaryButton: {
    backgroundColor: Colors.primary,
    borderRadius: 10,
    paddingVertical: 14,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 8,
  },
  buttonText: {
    fontSize: 16,
    fontWeight: '700',
    color: Colors.white,
    letterSpacing: 0.5,
  },
  helpText: {
    fontSize: 12,
    color: Colors.gray,
    textAlign: 'center',
    marginTop: 16,
    lineHeight: 18,
  },
  statsGrid: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 24,
  },
  statCard: {
    flex: 1,
    backgroundColor: Colors.white,
    borderRadius: 16,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.06,
    shadowRadius: 4,
    elevation: 2,
    position: 'relative',
  },
  statValue: {
    fontSize: 32,
    fontWeight: '700',
    color: Colors.primary,
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: Colors.gray,
    fontWeight: '500',
  },
  statBadge: {
    position: 'absolute',
    top: 12,
    right: 12,
    width: 36,
    height: 36,
    borderRadius: 12,
    backgroundColor: '#f0f4f8',
    justifyContent: 'center',
    alignItems: 'center',
  },
  guideBox: {
    backgroundColor: '#e8f1f7',
    borderRadius: 12,
    paddingVertical: 12,
    paddingHorizontal: 16,
    marginBottom: 20,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  guideText: {
    fontSize: 13,
    color: Colors.primary,
    fontWeight: '600',
  },
  actionCard: {
    backgroundColor: Colors.white,
    borderRadius: 14,
    paddingVertical: 16,
    paddingHorizontal: 16,
    marginBottom: 12,
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.06,
    shadowRadius: 4,
    elevation: 2,
  },
  actionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 2,
  },
  actionSubtitle: {
    fontSize: 12,
    color: Colors.gray,
    fontWeight: '400',
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#333',
    marginBottom: 12,
    marginTop: 12,
  },
  activityCard: {
    backgroundColor: Colors.white,
    borderRadius: 14,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.06,
    shadowRadius: 4,
    elevation: 2,
  },
  activityItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  activityDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: Colors.primary,
    marginTop: 6,
    marginRight: 12,
    flexShrink: 0,
  },
  activityTime: {
    fontSize: 11,
    color: Colors.gray,
    fontWeight: '500',
    marginBottom: 2,
  },
  activityDesc: {
    fontSize: 13,
    color: '#333',
    fontWeight: '500',
  },
  districtGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    justifyContent: 'space-between',
  },
  districtCard: {
    width: '48.5%',
    aspectRatio: 1,
    backgroundColor: Colors.white,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.06,
    shadowRadius: 4,
    elevation: 2,
    borderWidth: 2,
    borderColor: 'transparent',
  },
  districtCardSelected: {
    backgroundColor: Colors.primary,
    borderColor: Colors.dark,
  },
  districtName: {
    fontSize: 13,
    fontWeight: '700',
    color: '#333',
    textAlign: 'center',
  },
  districtCardSelected_districtName: {
    color: Colors.white,
  },
  progressBar: {
    height: 4,
    backgroundColor: Colors.lightGray,
    borderRadius: 2,
    marginBottom: 20,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: Colors.primary,
  },
  section: {
    backgroundColor: Colors.white,
    borderRadius: 14,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.06,
    shadowRadius: 4,
    elevation: 2,
  },
  sectionLabel: {
    fontSize: 14,
    fontWeight: '700',
    color: '#333',
    marginBottom: 12,
  },
  sectionDescription: {
    fontSize: 12,
    color: Colors.gray,
    marginBottom: 12,
  },
  typeGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  typeButton: {
    flex: 1,
    minWidth: '48%',
    paddingVertical: 10,
    backgroundColor: '#f9f9f9',
    borderWidth: 1.5,
    borderColor: Colors.lightGray,
    borderRadius: 8,
    alignItems: 'center',
  },
  typeButtonActive: {
    backgroundColor: Colors.primary,
    borderColor: Colors.primary,
  },
  typeButtonText: {
    fontSize: 13,
    color: '#666',
    fontWeight: '600',
  },
  typeButtonTextActive: {
    color: Colors.white,
  },
  textArea: {
    backgroundColor: '#f9f9f9',
    borderWidth: 1,
    borderColor: Colors.lightGray,
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 12,
    fontSize: 14,
    color: '#333',
    textAlignVertical: 'top',
    minHeight: 100,
  },
  imageUpload: {
    borderWidth: 2,
    borderStyle: 'dashed',
    borderColor: Colors.lightGray,
    borderRadius: 12,
    paddingVertical: 32,
    paddingHorizontal: 16,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#f9f9f9',
  },
  imageUploadText: {
    fontSize: 14,
    color: Colors.gray,
    fontWeight: '500',
  },
  statusGrid: {
    flexDirection: 'row',
    gap: 8,
  },
  statusButton: {
    flex: 1,
    paddingVertical: 12,
    backgroundColor: '#f9f9f9',
    borderWidth: 1.5,
    borderColor: Colors.lightGray,
    borderRadius: 10,
    alignItems: 'center',
  },
  statusButtonActive: {
    backgroundColor: Colors.primary,
    borderColor: Colors.primary,
  },
  statusButtonText: {
    fontSize: 13,
    color: '#666',
    fontWeight: '600',
  },
  statusButtonTextActive: {
    color: Colors.white,
  },
  buttonGroup: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 20,
  },
  settingCard: {
    backgroundColor: Colors.white,
    borderRadius: 14,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.06,
    shadowRadius: 4,
    elevation: 2,
    marginBottom: 12,
  },
  settingItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  settingLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 3,
  },
  settingDescription: {
    fontSize: 12,
    color: Colors.gray,
  },
  settingValue: {
    fontSize: 14,
    color: '#666',
    fontWeight: '500',
  },
  logoutButton: {
    backgroundColor: Colors.danger,
    borderRadius: 12,
    paddingVertical: 14,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 12,
    marginBottom: 32,
  },
  logoutButtonText: {
    fontSize: 16,
    fontWeight: '700',
    color: Colors.white,
  },
});
