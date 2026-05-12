import React, { useState } from 'react';
import {
  StyleSheet,
  View,
  Text,
  TextInput,
  TouchableOpacity,
  SafeAreaView,
  Alert,
  Dimensions,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';

const { width, height } = Dimensions.get('window');

export default function LoginScreen({ onLogin }) {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = async () => {
    if (!username || !password) {
      Alert.alert('입력 오류', '아이디와 비밀번호를 입력하세요.');
      return;
    }

    setIsLoading(true);
    
    // 애니메이션 효과 위해 0.5초 대기
    setTimeout(() => {
      if (username === 'admin' && password === 'admin123') {
        setIsLoading(false);
        onLogin();
      } else {
        setIsLoading(false);
        Alert.alert('로그인 실패', '아이디 또는 비밀번호가 올바르지 않습니다.');
      }
    }, 500);
  };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardContainer}
      >
        {/* 그래디언트 배경 */}
        <View style={styles.backgroundGradient}>
          {/* 상단 공간 */}
          <View style={styles.topSpace} />

          {/* 로그인 카드 */}
          <View style={styles.cardContainer}>
            {/* 로고 */}
            <View style={styles.logoSection}>
              <Text style={styles.logoEmoji}>🏛️</Text>
              <Text style={styles.appTitle}>메타도어</Text>
              <Text style={styles.appSubtitle}>유지보수 점검 시스템</Text>
            </View>

            {/* 폼 */}
            <View style={styles.formContainer}>
              {/* 아이디 입력 */}
              <View style={styles.formGroup}>
                <Text style={styles.formLabel}>아이디</Text>
                <View style={styles.inputWrapper}>
                  <TextInput
                    style={styles.formInput}
                    placeholder="아이디"
                    placeholderTextColor="#bbb"
                    value={username}
                    onChangeText={setUsername}
                    editable={!isLoading}
                  />
                </View>
              </View>

              {/* 비밀번호 입력 */}
              <View style={styles.formGroup}>
                <Text style={styles.formLabel}>비밀번호</Text>
                <View style={styles.inputWrapper}>
                  <TextInput
                    style={styles.formInput}
                    placeholder="비밀번호"
                    placeholderTextColor="#bbb"
                    value={password}
                    onChangeText={setPassword}
                    secureTextEntry
                    editable={!isLoading}
                  />
                </View>
              </View>

              {/* 로그인 버튼 */}
              <TouchableOpacity
                style={[styles.loginButton, isLoading && styles.loginButtonDisabled]}
                onPress={handleLogin}
                activeOpacity={0.8}
                disabled={isLoading}
              >
                <Text style={styles.loginButtonText}>
                  {isLoading ? '로그인 중...' : '로그인'}
                </Text>
              </TouchableOpacity>

              {/* 도움말 */}
              <Text style={styles.helpText}>
                권한자가 등록한 직원만{'\n'}로그인할 수 있습니다.
              </Text>
            </View>
          </View>

          {/* 하단 공간 */}
          <View style={styles.bottomSpace} />
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1e5a96',
  },
  keyboardContainer: {
    flex: 1,
  },
  backgroundGradient: {
    flex: 1,
    backgroundColor: '#1e5a96',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
  },
  topSpace: {
    flex: 0.5,
    justifyContent: 'flex-end',
  },
  bottomSpace: {
    flex: 0.3,
  },
  cardContainer: {
    backgroundColor: '#ffffff',
    borderRadius: 20,
    paddingVertical: 40,
    paddingHorizontal: 24,
    shadowColor: '#000000',
    shadowOffset: {
      width: 0,
      height: 10,
    },
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
    color: '#333333',
    marginBottom: 6,
    letterSpacing: -0.5,
  },
  appSubtitle: {
    fontSize: 14,
    color: '#999999',
    fontWeight: '400',
  },
  formContainer: {
    gap: 20,
  },
  formGroup: {
    gap: 8,
  },
  formLabel: {
    fontSize: 13,
    fontWeight: '600',
    color: '#333333',
    letterSpacing: 0.3,
  },
  inputWrapper: {
    borderRadius: 10,
    overflow: 'hidden',
    backgroundColor: '#f8f8f8',
  },
  formInput: {
    paddingHorizontal: 16,
    paddingVertical: 14,
    fontSize: 15,
    color: '#333333',
    backgroundColor: '#f8f8f8',
  },
  loginButton: {
    backgroundColor: '#1e5a96',
    borderRadius: 10,
    paddingVertical: 14,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 8,
    shadowColor: '#1e5a96',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 5,
  },
  loginButtonDisabled: {
    opacity: 0.7,
  },
  loginButtonText: {
    fontSize: 16,
    fontWeight: '700',
    color: '#ffffff',
    letterSpacing: 0.5,
  },
  helpText: {
    fontSize: 12,
    color: '#999999',
    textAlign: 'center',
    lineHeight: 18,
    marginTop: 4,
  },
});
