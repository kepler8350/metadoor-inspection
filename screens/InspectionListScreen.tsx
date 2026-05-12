import React, { useState } from 'react';
import {
  StyleSheet,
  View,
  Text,
  TouchableOpacity,
  SafeAreaView,
  ScrollView,
  StatusBar,
} from 'react-native';

export default function InspectionListScreen({ navigation }) {
  const [selectedDistrict, setSelectedDistrict] = useState(null);

  const handleSelectDistrict = (district) => {
    setSelectedDistrict(district);
    setTimeout(() => {
      navigation.navigate('InspectionDetail', {
        mode: 'create',
        selectedDistrict: district,
      });
    }, 200);
  };

  const districts = [
    { name: '금정구', icon: '🏢' },
    { name: '기장군', icon: '🌳' },
    { name: '남구', icon: '🏖️' },
    { name: '동구', icon: '🏭' },
    { name: '동래구', icon: '🏗️' },
    { name: '부산진구', icon: '🏙️' },
    { name: '북구', icon: '🌲' },
    { name: '사상구', icon: '🏘️' },
    { name: '사하구', icon: '🌉' },
    { name: '서구', icon: '🏛️' },
    { name: '수영구', icon: '🏊' },
    { name: '연제구', icon: '🌳' },
    { name: '영도구', icon: '⛵' },
    { name: '중구', icon: '🏢' },
    { name: '해운대구', icon: '🏖️' },
  ];

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
          <Text style={styles.headerTitle}>점검 위치 선택</Text>
          <Text style={styles.headerSubtitle}>2단계 / 3단계</Text>
        </View>
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* 지침 텍스트 */}
        <View style={styles.guideBox}>
          <Text style={styles.guideIcon}>📍</Text>
          <Text style={styles.guideText}>점검할 지역을 선택하세요</Text>
        </View>

        {/* 지역 그리드 */}
        <View style={styles.districtGrid}>
          {districts.map((district, index) => (
            <TouchableOpacity
              key={index}
              style={[
                styles.districtCard,
                selectedDistrict === district.name && styles.districtCardSelected,
              ]}
              onPress={() => handleSelectDistrict(district.name)}
              activeOpacity={0.7}
            >
              <Text style={styles.districtIcon}>{district.icon}</Text>
              <Text style={styles.districtName}>{district.name}</Text>
            </TouchableOpacity>
          ))}
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
  guideIcon: {
    fontSize: 20,
  },
  guideText: {
    fontSize: 13,
    color: '#1e5a96',
    fontWeight: '600',
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
    backgroundColor: '#ffffff',
    borderRadius: 14,
    paddingVertical: 16,
    paddingHorizontal: 12,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.06,
    shadowRadius: 4,
    elevation: 2,
    borderWidth: 2,
    borderColor: 'transparent',
  },
  districtCardSelected: {
    backgroundColor: '#1e5a96',
    borderColor: '#164a7a',
  },
  districtIcon: {
    fontSize: 32,
    marginBottom: 8,
  },
  districtName: {
    fontSize: 13,
    fontWeight: '700',
    color: '#333333',
    textAlign: 'center',
  },
  districtCardSelected_districtName: {
    color: '#ffffff',
  },
});
