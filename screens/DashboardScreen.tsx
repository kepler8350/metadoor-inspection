import React, { useState } from 'react';
import {
  StyleSheet,
  View,
  Text,
  TouchableOpacity,
  SafeAreaView,
  ScrollView,
  Dimensions,
  StatusBar,
} from 'react-native';

const { width } = Dimensions.get('window');

export default function DashboardScreen({ navigation }) {
  const [stats, setStats] = useState({
    totalInspections: 5,
    thisMonthInspections: 2,
  });

  const handleNewInspection = () => {
    navigation.navigate('Inspection', {
      screen: 'InspectionList',
    });
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#1e5a96" />
      
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {/* 헤더 */}
        <View style={styles.header}>
          <View>
            <Text style={styles.headerTitle}>대시보드</Text>
            <Text style={styles.headerSubtitle}>admin님 환영합니다!</Text>
          </View>
          <TouchableOpacity style={styles.userButton}>
            <Text style={styles.userIcon}>👤</Text>
          </TouchableOpacity>
        </View>

        {/* 컨텐츠 */}
        <View style={styles.content}>
          {/* 통계 카드 */}
          <View style={styles.statsContainer}>
            <View style={styles.statCard}>
              <Text style={styles.statValue}>{stats.totalInspections}</Text>
              <Text style={styles.statLabel}>총 점검 횟수</Text>
              <View style={styles.statBadge}>
                <Text style={styles.statBadgeText}>📊</Text>
              </View>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statValue}>{stats.thisMonthInspections}</Text>
              <Text style={styles.statLabel}>이달 점검</Text>
              <View style={styles.statBadge}>
                <Text style={styles.statBadgeText}>📅</Text>
              </View>
            </View>
          </View>

          {/* 액션 버튼 */}
          <View style={styles.actionsContainer}>
            <TouchableOpacity
              style={[styles.actionCard, styles.primaryAction]}
              onPress={handleNewInspection}
              activeOpacity={0.7}
            >
              <View style={styles.actionIcon}>
                <Text style={styles.actionIconText}>✏️</Text>
              </View>
              <View style={styles.actionContent}>
                <Text style={styles.actionTitle}>새 점검 입력</Text>
                <Text style={styles.actionSubtitle}>오늘의 점검을 시작하세요</Text>
              </View>
              <Text style={styles.actionArrow}>›</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.actionCard}
              activeOpacity={0.7}
            >
              <View style={styles.actionIcon}>
                <Text style={styles.actionIconText}>📋</Text>
              </View>
              <View style={styles.actionContent}>
                <Text style={styles.actionTitle}>점검 이력</Text>
                <Text style={styles.actionSubtitle}>지난 점검 기록 보기</Text>
              </View>
              <Text style={styles.actionArrow}>›</Text>
            </TouchableOpacity>
          </View>

          {/* 최근 활동 */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>최근 활동</Text>
            <View style={styles.activityCard}>
              <View style={styles.activityItem}>
                <View style={styles.activityDot} />
                <View style={styles.activityContent}>
                  <Text style={styles.activityTime}>오늘 14:30</Text>
                  <Text style={styles.activityDesc}>사상구 - 외벽 점검 완료</Text>
                </View>
              </View>
              <View style={[styles.activityItem, { marginTop: 12, paddingTop: 12, borderTopWidth: 1, borderTopColor: '#f0f0f0' }]}>
                <View style={styles.activityDot} />
                <View style={styles.activityContent}>
                  <Text style={styles.activityTime}>어제 10:15</Text>
                  <Text style={styles.activityDesc}>부산진구 - 지붕 점검 완료</Text>
                </View>
              </View>
            </View>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f7fa',
  },
  scrollView: {
    flex: 1,
  },
  header: {
    backgroundColor: '#1e5a96',
    paddingHorizontal: 20,
    paddingTop: 16,
    paddingBottom: 24,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
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
  userButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  userIcon: {
    fontSize: 20,
  },
  content: {
    paddingHorizontal: 20,
    paddingVertical: 24,
  },
  statsContainer: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 24,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#ffffff',
    borderRadius: 16,
    padding: 20,
    shadowColor: '#000000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.06,
    shadowRadius: 4,
    elevation: 2,
    position: 'relative',
  },
  statValue: {
    fontSize: 32,
    fontWeight: '700',
    color: '#1e5a96',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#999999',
    fontWeight: '500',
    letterSpacing: 0.3,
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
  statBadgeText: {
    fontSize: 18,
  },
  actionsContainer: {
    gap: 12,
    marginBottom: 24,
  },
  actionCard: {
    backgroundColor: '#ffffff',
    borderRadius: 14,
    paddingVertical: 16,
    paddingHorizontal: 16,
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: '#000000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.06,
    shadowRadius: 4,
    elevation: 2,
  },
  primaryAction: {
    backgroundColor: '#1e5a96',
  },
  actionIcon: {
    width: 44,
    height: 44,
    borderRadius: 12,
    backgroundColor: 'rgba(30, 90, 150, 0.1)',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  primaryAction_actionIcon: {
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
  },
  actionIconText: {
    fontSize: 20,
  },
  actionContent: {
    flex: 1,
  },
  actionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333333',
    marginBottom: 2,
  },
  primaryAction_actionTitle: {
    color: '#ffffff',
  },
  actionSubtitle: {
    fontSize: 12,
    color: '#999999',
    fontWeight: '400',
  },
  primaryAction_actionSubtitle: {
    color: 'rgba(255, 255, 255, 0.7)',
  },
  actionArrow: {
    fontSize: 20,
    color: '#cccccc',
    marginLeft: 8,
  },
  primaryAction_actionArrow: {
    color: 'rgba(255, 255, 255, 0.5)',
  },
  section: {
    marginTop: 12,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#333333',
    marginBottom: 12,
  },
  activityCard: {
    backgroundColor: '#ffffff',
    borderRadius: 14,
    padding: 16,
    shadowColor: '#000000',
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
    backgroundColor: '#1e5a96',
    marginTop: 6,
    marginRight: 12,
    flexShrink: 0,
  },
  activityContent: {
    flex: 1,
  },
  activityTime: {
    fontSize: 11,
    color: '#999999',
    fontWeight: '500',
    marginBottom: 2,
  },
  activityDesc: {
    fontSize: 13,
    color: '#333333',
    fontWeight: '500',
  },
});
