import React, { useState } from 'react';
import {
  StyleSheet,
  View,
  Text,
  TouchableOpacity,
  SafeAreaView,
  ScrollView,
  Switch,
  StatusBar,
  Alert,
} from 'react-native';

export default function SettingsScreen({ navigation }) {
  const [notifications, setNotifications] = useState(true);
  const [darkMode, setDarkMode] = useState(false);

  const handleLogout = () => {
    Alert.alert('로그아웃', '정말 로그아웃 하시겠습니까?', [
      { text: '취소', onPress: () => {} },
      {
        text: '로그아웃',
        onPress: () => {
          // 로그아웃 처리
          navigation.navigate('Login');
        },
        style: 'destructive',
      },
    ]);
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#1e5a96" />

      {/* 헤더 */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>설정</Text>
        <Text style={styles.headerSubtitle}>앱 설정 및 정보</Text>
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* 계정 섹션 */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>계정</Text>
          <View style={styles.settingCard}>
            <View style={styles.settingItem}>
              <View style={styles.settingLeft}>
                <Text style={styles.settingLabel}>사용자명</Text>
                <Text style={styles.settingValue}>admin</Text>
              </View>
              <Text style={styles.settingIcon}>👤</Text>
            </View>
            <View style={[styles.settingItem, { borderTopWidth: 1, borderTopColor: '#f0f0f0', paddingTop: 12, marginTop: 12 }]}>
              <View style={styles.settingLeft}>
                <Text style={styles.settingLabel}>역할</Text>
                <Text style={styles.settingValue}>관리자</Text>
              </View>
              <Text style={styles.settingIcon}>👨‍💼</Text>
            </View>
          </View>
        </View>

        {/* 알림 섹션 */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>알림</Text>
          <View style={styles.settingCard}>
            <View style={styles.settingItem}>
              <View style={styles.settingLeft}>
                <Text style={styles.settingLabel}>푸시 알림</Text>
                <Text style={styles.settingDescription}>점검 완료 시 알림</Text>
              </View>
              <Switch
                value={notifications}
                onValueChange={setNotifications}
                trackColor={{ false: '#ddd', true: '#81c784' }}
                thumbColor={notifications ? '#1e5a96' : '#999'}
              />
            </View>
          </View>
        </View>

        {/* 화면 섹션 */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>화면</Text>
          <View style={styles.settingCard}>
            <View style={styles.settingItem}>
              <View style={styles.settingLeft}>
                <Text style={styles.settingLabel}>다크 모드</Text>
                <Text style={styles.settingDescription}>야간 모드</Text>
              </View>
              <Switch
                value={darkMode}
                onValueChange={setDarkMode}
                trackColor={{ false: '#ddd', true: '#81c784' }}
                thumbColor={darkMode ? '#1e5a96' : '#999'}
              />
            </View>
          </View>
        </View>

        {/* 정보 섹션 */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>정보</Text>
          <View style={styles.settingCard}>
            <View style={styles.settingItem}>
              <View style={styles.settingLeft}>
                <Text style={styles.settingLabel}>앱 버전</Text>
              </View>
              <Text style={styles.settingValue}>1.0.0</Text>
            </View>
            <View style={[styles.settingItem, { borderTopWidth: 1, borderTopColor: '#f0f0f0', paddingTop: 12, marginTop: 12 }]}>
              <View style={styles.settingLeft}>
                <Text style={styles.settingLabel}>빌드 번호</Text>
              </View>
              <Text style={styles.settingValue}>001</Text>
            </View>
            <View style={[styles.settingItem, { borderTopWidth: 1, borderTopColor: '#f0f0f0', paddingTop: 12, marginTop: 12 }]}>
              <View style={styles.settingLeft}>
                <Text style={styles.settingLabel}>업데이트 확인</Text>
              </View>
              <Text style={styles.settingArrow}>›</Text>
            </View>
          </View>
        </View>

        {/* 도움말 섹션 */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>도움말</Text>
          <View style={styles.settingCard}>
            <TouchableOpacity style={styles.settingItem} activeOpacity={0.6}>
              <View style={styles.settingLeft}>
                <Text style={styles.settingLabel}>이용약관</Text>
              </View>
              <Text style={styles.settingArrow}>›</Text>
            </TouchableOpacity>
            <View style={[styles.settingItem, { borderTopWidth: 1, borderTopColor: '#f0f0f0', paddingTop: 12, marginTop: 12 }]}>
              <TouchableOpacity activeOpacity={0.6} style={{ flex: 1 }}>
                <View style={styles.settingLeft}>
                  <Text style={styles.settingLabel}>개인정보보호정책</Text>
                </View>
              </TouchableOpacity>
              <Text style={styles.settingArrow}>›</Text>
            </TouchableOpacity>
            <View style={[styles.settingItem, { borderTopWidth: 1, borderTopColor: '#f0f0f0', paddingTop: 12, marginTop: 12 }]}>
              <TouchableOpacity activeOpacity={0.6} style={{ flex: 1 }}>
                <View style={styles.settingLeft}>
                  <Text style={styles.settingLabel}>고객 지원</Text>
                </View>
              </TouchableOpacity>
              <Text style={styles.settingArrow}>›</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* 로그아웃 버튼 */}
        <TouchableOpacity
          style={styles.logoutButton}
          onPress={handleLogout}
          activeOpacity={0.7}
        >
          <Text style={styles.logoutButtonText}>로그아웃</Text>
        </TouchableOpacity>

        <View style={{ height: 20 }} />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f7fa',
  },
  header: {
    backgroundColor: '#1e5a96',
    paddingHorizontal: 20,
    paddingVertical: 20,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: '700',
    color: '#ffffff',
    marginBottom: 4,
    letterSpacing: -0.5,
  },
  headerSubtitle: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.7)',
    fontWeight: '400',
  },
  content: {
    flex: 1,
    paddingHorizontal: 16,
    paddingVertical: 16,
  },
  section: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 13,
    fontWeight: '700',
    color: '#666666',
    marginBottom: 12,
    textTransform: 'uppercase',
    letterSpacing: 0.3,
  },
  settingCard: {
    backgroundColor: '#ffffff',
    borderRadius: 14,
    padding: 16,
    shadowColor: '#000000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.06,
    shadowRadius: 4,
    elevation: 2,
  },
  settingItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  settingLeft: {
    flex: 1,
  },
  settingLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333333',
    marginBottom: 3,
  },
  settingDescription: {
    fontSize: 12,
    color: '#999999',
    fontWeight: '400',
  },
  settingValue: {
    fontSize: 14,
    color: '#666666',
    fontWeight: '500',
  },
  settingIcon: {
    fontSize: 20,
    marginLeft: 12,
  },
  settingArrow: {
    fontSize: 18,
    color: '#999999',
    marginLeft: 12,
  },
  logoutButton: {
    backgroundColor: '#ff6b6b',
    borderRadius: 12,
    paddingVertical: 14,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 12,
    shadowColor: '#ff6b6b',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 3,
  },
  logoutButtonText: {
    fontSize: 16,
    fontWeight: '700',
    color: '#ffffff',
    letterSpacing: 0.5,
  },
});
