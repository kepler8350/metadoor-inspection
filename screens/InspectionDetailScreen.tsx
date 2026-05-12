import React, { useState } from 'react';
import {
  StyleSheet,
  View,
  Text,
  TextInput,
  TouchableOpacity,
  SafeAreaView,
  ScrollView,
  Alert,
  Image,
  Picker,
  StatusBar,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';

export default function InspectionDetailScreen({ route, navigation }) {
  const [selectedDistrict, setSelectedDistrict] = useState(
    route?.params?.selectedDistrict || '사상구'
  );
  const [inspectionType, setInspectionType] = useState('');
  const [content, setContent] = useState('');
  const [status, setStatus] = useState('정상');
  const [image, setImage] = useState(null);

  const handleSelectImage = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [4, 3],
      quality: 1,
    });

    if (!result.cancelled) {
      setImage(result.assets[0].uri);
    }
  };

  const handleTakePhoto = async () => {
    const result = await ImagePicker.launchCameraAsync({
      allowsEditing: true,
      aspect: [4, 3],
      quality: 1,
    });

    if (!result.cancelled) {
      setImage(result.assets[0].uri);
    }
  };

  const handleSubmit = () => {
    if (!inspectionType) {
      Alert.alert('입력 오류', '점검 항목을 선택하세요.');
      return;
    }

    Alert.alert('✓ 완료', '점검이 저장되었습니다.', [
      {
        text: '확인',
        onPress: () => {
          navigation.navigate('Dashboard');
        },
      },
    ]);
  };

  const handleSave = () => {
    Alert.alert('저장됨', '점검이 임시 저장되었습니다.');
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#1e5a96" />
      
      {/* 헤더 */}
      <View style={styles.header}>
        <TouchableOpacity
          onPress={() => navigation.goBack()}
          style={styles.backButton}
        >
          <Text style={styles.backButtonText}>‹</Text>
        </TouchableOpacity>
        <View style={styles.headerContent}>
          <Text style={styles.headerTitle}>점검 입력</Text>
          <Text style={styles.headerSubtitle}>
            {selectedDistrict} - 점검 입력 / 3단계
          </Text>
        </View>
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* 진행률 인디케이터 */}
        <View style={styles.progressBar}>
          <View style={[styles.progressFill, { width: '66%' }]} />
        </View>

        {/* 점검 항목 섹션 */}
        <View style={styles.section}>
          <Text style={styles.sectionLabel}>점검 항목</Text>
          <View style={styles.pickerWrapper}>
            <Picker
              selectedValue={inspectionType}
              onValueChange={(itemValue) => setInspectionType(itemValue)}
              style={styles.picker}
            >
              <Picker.Item label="-- 항목 선택 --" value="" />
              <Picker.Item label="🏗️ 외벽" value="외벽" />
              <Picker.Item label="🏠 지붕" value="지붕" />
              <Picker.Item label="🪟 창호" value="창호" />
              <Picker.Item label="⬇️ 바닥" value="바닥" />
              <Picker.Item label="🎨 내벽" value="내벽" />
              <Picker.Item label="❓ 기타" value="기타" />
            </Picker>
          </View>
        </View>

        {/* 조사 내용 섹션 */}
        <View style={styles.section}>
          <Text style={styles.sectionLabel}>조사 내용</Text>
          <Text style={styles.sectionDescription}>
            이상 발견 시 조사 내용을 기록하세요
          </Text>
          <TextInput
            style={styles.textAreaInput}
            placeholder="예: 페널 박인 → 조기화 완료"
            placeholderTextColor="#bbb"
            multiline
            numberOfLines={4}
            value={content}
            onChangeText={setContent}
          />
        </View>

        {/* 사진 섹션 */}
        <View style={styles.section}>
          <Text style={styles.sectionLabel}>사진</Text>
          {image ? (
            <View style={styles.imageContainer}>
              <Image
                source={{ uri: image }}
                style={styles.imagePreview}
              />
              <TouchableOpacity
                style={styles.removeImageButton}
                onPress={() => setImage(null)}
              >
                <Text style={styles.removeImageButtonText}>제거</Text>
              </TouchableOpacity>
            </View>
          ) : (
            <TouchableOpacity
              style={styles.imageUploadArea}
              onPress={handleSelectImage}
            >
              <Text style={styles.imageUploadIcon}>📷</Text>
              <Text style={styles.imageUploadText}>사진 추가</Text>
            </TouchableOpacity>
          )}
          <View style={styles.imageButtonGroup}>
            <TouchableOpacity
              style={styles.imageButton}
              onPress={handleSelectImage}
            >
              <Text style={styles.imageButtonIcon}>🖼️</Text>
              <Text style={styles.imageButtonText}>갤러리</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={styles.imageButton}
              onPress={handleTakePhoto}
            >
              <Text style={styles.imageButtonIcon}>📸</Text>
              <Text style={styles.imageButtonText}>카메라</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* 점검 상태 섹션 */}
        <View style={styles.section}>
          <Text style={styles.sectionLabel}>점검 상태</Text>
          <View style={styles.statusContainer}>
            {['정상', '요주의', '이상'].map((statusOption) => (
              <TouchableOpacity
                key={statusOption}
                style={[
                  styles.statusButton,
                  status === statusOption && styles.statusButtonActive,
                ]}
                onPress={() => setStatus(statusOption)}
              >
                <Text
                  style={[
                    styles.statusButtonText,
                    status === statusOption && styles.statusButtonTextActive,
                  ]}
                >
                  {statusOption === '정상' && '✓ '}
                  {statusOption === '요주의' && '! '}
                  {statusOption === '이상' && '✕ '}
                  {statusOption}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* 버튼 그룹 */}
        <View style={styles.buttonGroup}>
          <TouchableOpacity
            style={[styles.button, styles.secondaryButton]}
            onPress={handleSave}
            activeOpacity={0.7}
          >
            <Text style={styles.secondaryButtonText}>임시 저장</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.button, styles.primaryButton]}
            onPress={handleSubmit}
            activeOpacity={0.7}
          >
            <Text style={styles.primaryButtonText}>완료</Text>
          </TouchableOpacity>
        </View>

        <View style={{ height: 24 }} />
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
    paddingHorizontal: 16,
    paddingVertical: 16,
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 12,
  },
  backButton: {
    width: 32,
    height: 32,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 4,
  },
  backButtonText: {
    fontSize: 28,
    color: '#ffffff',
    fontWeight: '300',
  },
  headerContent: {
    flex: 1,
  },
  headerTitle: {
    fontSize: 22,
    fontWeight: '700',
    color: '#ffffff',
    marginBottom: 2,
  },
  headerSubtitle: {
    fontSize: 12,
    color: 'rgba(255, 255, 255, 0.7)',
    fontWeight: '400',
  },
  content: {
    flex: 1,
    paddingHorizontal: 16,
    paddingTop: 16,
  },
  progressBar: {
    height: 4,
    backgroundColor: '#e0e0e0',
    borderRadius: 2,
    marginBottom: 20,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#1e5a96',
  },
  section: {
    backgroundColor: '#ffffff',
    borderRadius: 14,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.06,
    shadowRadius: 4,
    elevation: 2,
  },
  sectionLabel: {
    fontSize: 14,
    fontWeight: '700',
    color: '#333333',
    marginBottom: 12,
    letterSpacing: 0.3,
  },
  sectionDescription: {
    fontSize: 12,
    color: '#999999',
    marginBottom: 12,
    fontWeight: '400',
  },
  pickerWrapper: {
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 10,
    overflow: 'hidden',
    backgroundColor: '#f9f9f9',
  },
  picker: {
    height: 50,
  },
  textAreaInput: {
    backgroundColor: '#f9f9f9',
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 12,
    fontSize: 14,
    color: '#333333',
    textAlignVertical: 'top',
    fontFamily: 'System',
  },
  imageUploadArea: {
    borderWidth: 2,
    borderStyle: 'dashed',
    borderColor: '#ddd',
    borderRadius: 12,
    paddingVertical: 32,
    paddingHorizontal: 16,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#f9f9f9',
    marginBottom: 12,
  },
  imageUploadIcon: {
    fontSize: 36,
    marginBottom: 8,
  },
  imageUploadText: {
    fontSize: 14,
    color: '#999999',
    fontWeight: '500',
  },
  imageContainer: {
    marginBottom: 12,
  },
  imagePreview: {
    width: '100%',
    height: 200,
    borderRadius: 12,
    backgroundColor: '#f0f0f0',
    marginBottom: 12,
  },
  removeImageButton: {
    paddingVertical: 10,
    backgroundColor: '#ff6b6b',
    borderRadius: 8,
    alignItems: 'center',
  },
  removeImageButtonText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '600',
  },
  imageButtonGroup: {
    flexDirection: 'row',
    gap: 12,
  },
  imageButton: {
    flex: 1,
    paddingVertical: 12,
    backgroundColor: '#f9f9f9',
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 10,
    alignItems: 'center',
    gap: 4,
  },
  imageButtonIcon: {
    fontSize: 18,
  },
  imageButtonText: {
    fontSize: 13,
    color: '#666666',
    fontWeight: '600',
  },
  statusContainer: {
    flexDirection: 'row',
    gap: 8,
  },
  statusButton: {
    flex: 1,
    paddingVertical: 12,
    backgroundColor: '#f9f9f9',
    borderWidth: 1.5,
    borderColor: '#e0e0e0',
    borderRadius: 10,
    alignItems: 'center',
  },
  statusButtonActive: {
    backgroundColor: '#1e5a96',
    borderColor: '#1e5a96',
  },
  statusButtonText: {
    fontSize: 13,
    color: '#666666',
    fontWeight: '600',
  },
  statusButtonTextActive: {
    color: '#ffffff',
  },
  buttonGroup: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 20,
  },
  button: {
    flex: 1,
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  primaryButton: {
    backgroundColor: '#1e5a96',
  },
  primaryButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '700',
    letterSpacing: 0.5,
  },
  secondaryButton: {
    backgroundColor: '#e8e8e8',
  },
  secondaryButtonText: {
    color: '#666666',
    fontSize: 16,
    fontWeight: '700',
    letterSpacing: 0.5,
  },
});
