import os
import json
from flask import Flask, render_template_string, request, session, jsonify, redirect
import sqlite3
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'metadoor-secret-key-2024'
DB_PATH = '/tmp/metadoor.db'

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'
USER_USERNAME = 'user'
USER_PASSWORD = 'user123'

# 11개 점검 항목
INSPECTION_ITEMS = ['패널', '보드', '전원', 'PC', '카메라', '스피커', '마이크', '입력장치', '하우징', '외관데코', '기타']

# 메타도어 설치 데이터 (40개)
METADOOR_DATA = {
    '금정구': ['금정구청', '금정도서관', '금정보건소'],
    '기장군': ['기장군청', '기장도서관', '정관중학교'],
    '남구': ['남구청', '용호문화센터', '남부경찰서'],
    '동구': ['동구청', '초량문화센터', '동부경찰서'],
    '동래구': ['동래구청', '동래도서관', '온천장센터'],
    '부산진구': ['부산진구청', '부산진도서관', '서면문화센터'],
    '북구': ['북구청', '북부도서관', '구포센터'],
    '사상구': ['사상구청', '사상도서관', '삼락공원'],
    '사하구': ['사하구청', '감천문화마을', '사하도서관'],
    '서구': ['서구청', '암남공원', '서부센터'],
    '수영구': ['수영구청', '수영도서관', '광안리관리소'],
    '연제구': ['연제구청', '연제도서관', '연제센터'],
    '영도구': ['영도구청', '영도도서관', '절영로역사관'],
    '중구': ['중구청', '중앙도서관', '항만공사'],
    '해운대구': ['해운대구청', '해운대도서관', '해수욕장관리소']
}

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS field_inspections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            district TEXT,
            location TEXT,
            month INTEGER,
            year INTEGER,
            status TEXT,
            action_content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS remote_inspections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            district TEXT,
            location TEXT,
            item TEXT,
            month INTEGER,
            year INTEGER,
            status TEXT,
            detail_content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

# ===== 사용자 모바일 앱 =====
USER_APP_HTML = '''
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>메타도어 점검 앱</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f7fa; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 10px; }
    .mobile-frame { width: 100%; max-width: 375px; height: 812px; background: white; border-radius: 40px; border: 12px solid #000; box-shadow: 0 20px 60px rgba(0,0,0,0.3); overflow: hidden; display: flex; flex-direction: column; }
    .notch { background: #000; height: 28px; display: flex; justify-content: center; align-items: center; font-size: 11px; color: white; }
    .status-bar { background: #000; color: white; padding: 4px 16px; font-size: 11px; display: flex; justify-content: space-between; align-items: center; height: 24px; }
    .app-content { flex: 1; display: flex; flex-direction: column; background: white; overflow: hidden; }
    .screen { flex: 1; display: none; flex-direction: column; overflow: hidden; }
    .screen.active { display: flex; }
    
    .login-screen { background: linear-gradient(135deg, #1e5a96 0%, #164a7a 100%); padding: 0; justify-content: center; align-items: center; }
    .login-container { text-align: center; padding: 40px 24px; width: 100%; }
    .logo { font-size: 56px; margin-bottom: 16px; }
    .title { font-size: 28px; font-weight: 700; color: white; margin-bottom: 8px; }
    .subtitle { font-size: 13px; color: rgba(255, 255, 255, 0.7); margin-bottom: 32px; }
    .login-card { background: white; border-radius: 16px; padding: 28px 24px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); }
    .input-group { margin-bottom: 16px; }
    .label { display: block; font-size: 12px; font-weight: 600; color: #333; margin-bottom: 6px; }
    input { width: 100%; padding: 11px 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; font-family: inherit; }
    input:focus { outline: none; border-color: #1e5a96; }
    .btn { width: 100%; padding: 12px; border: none; border-radius: 8px; font-size: 15px; font-weight: 700; cursor: pointer; font-family: inherit; }
    .btn-primary { background: #1e5a96; color: white; }
    .btn-primary:active { background: #164a7a; }
    
    .inspection-screen { padding: 16px; overflow-y: auto; }
    .inspection-header { background: #1e5a96; color: white; padding: 16px; border-radius: 12px; margin-bottom: 16px; text-align: center; }
    .form-group { background: #f9f9f9; border-radius: 8px; padding: 12px; margin-bottom: 10px; }
    .form-title { font-size: 12px; font-weight: 600; color: #333; margin-bottom: 8px; }
    select, textarea { width: 100%; padding: 9px; border: 1px solid #ddd; border-radius: 6px; font-size: 13px; font-family: inherit; }
    textarea { resize: vertical; min-height: 70px; }
    .button-group { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 16px; }
    .btn-secondary { background: #e0e0e0; color: #333; }
  </style>
</head>
<body>
  <div class="mobile-frame">
    <div class="notch">9:41</div>
    <div class="status-bar"><span>📶</span><span>🔋</span></div>
    <div class="app-content">
      <div class="screen login-screen active">
        <div class="login-container">
          <div class="logo">🏛️</div>
          <div class="title">메타도어</div>
          <div class="subtitle">유지보수 점검 시스템</div>
          <div class="login-card">
            <div class="input-group">
              <label class="label">아이디</label>
              <input type="text" id="username" value="user" placeholder="아이디">
            </div>
            <div class="input-group">
              <label class="label">비밀번호</label>
              <input type="password" id="password" value="user123" placeholder="비밀번호">
            </div>
            <button class="btn btn-primary" onclick="handleLogin()">로그인</button>
          </div>
        </div>
      </div>
      
      <div class="screen inspection-screen">
        <div class="inspection-header">
          <div style="font-size: 20px; font-weight: 700; margin-bottom: 4px;">사상구 - 사상도서관</div>
          <div style="font-size: 12px; color: rgba(255, 255, 255, 0.8);">점검 입력 / 3단계</div>
        </div>
        
        <div class="form-group">
          <div class="form-title">점검 항목</div>
          <select id="insp-item">
            <option value="">-- 선택하세요 --</option>
          </select>
        </div>
        
        <div class="form-group">
          <div class="form-title">조사 내용</div>
          <textarea id="insp-content" placeholder="이상 발견 시 조사 내용 기록"></textarea>
        </div>
        
        <div class="form-group">
          <div class="form-title">점검 상태</div>
          <select id="insp-status">
            <option value="정상">✓ 정상</option>
            <option value="이상">✕ 이상</option>
          </select>
        </div>
        
        <div class="button-group">
          <button class="btn btn-secondary" onclick="handleSave()">저장</button>
          <button class="btn btn-primary" onclick="handleSubmit()">완료</button>
        </div>
      </div>
    </div>
  </div>
  
  <script>
    const INSPECTION_ITEMS = ''' + json.dumps(INSPECTION_ITEMS, ensure_ascii=False) + ''';
    
    function handleLogin() {
      const username = document.getElementById('username').value;
      const password = document.getElementById('password').value;
      if (username === 'user' && password === 'user123') {
        window.location.href = '/app/inspection';
      } else {
        alert('로그인 실패');
      }
    }
    
    function initInspectionItems() {
      const select = document.getElementById('insp-item');
      INSPECTION_ITEMS.forEach(item => {
        const option = document.createElement('option');
        option.value = item;
        option.textContent = item;
        select.appendChild(option);
      });
    }
    
    function handleSave() { alert('저장되었습니다.'); }
    function handleSubmit() { alert('점검이 완료되었습니다!'); window.location.href = '/'; }
    
    initInspectionItems();
  </script>
</body>
</html>
'''

# ===== 관리자 대시보드 =====
ADMIN_DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>메타도어 - 관리자</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f7fa; }
    
    .header { background: linear-gradient(135deg, #1e5a96 0%, #164a7a 100%); color: white; padding: 20px; display: flex; justify-content: space-between; align-items: center; }
    .header-title { font-size: 24px; font-weight: 700; }
    .logout-btn { background: rgba(255,255,255,0.2); border: 1px solid rgba(255,255,255,0.3); color: white; padding: 8px 16px; border-radius: 6px; cursor: pointer; }
    
    .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
    
    .menu-tabs { display: flex; gap: 10px; margin-bottom: 20px; border-bottom: 2px solid #ddd; }
    .menu-tab { padding: 12px 20px; background: none; border: none; font-size: 16px; font-weight: 600; color: #666; cursor: pointer; border-bottom: 3px solid transparent; }
    .menu-tab.active { color: #1e5a96; border-bottom-color: #1e5a96; }
    
    .content { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
    .content.hidden { display: none; }
    
    .table { width: 100%; border-collapse: collapse; }
    .table th { padding: 12px; text-align: left; font-weight: 600; background: #f9f9f9; border-bottom: 2px solid #eee; }
    .table td { padding: 12px; border-bottom: 1px solid #eee; }
    .table tr:hover { background: #f9f9f9; }
    
    .stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 20px; }
    .stat-card { background: linear-gradient(135deg, #1e5a96 0%, #164a7a 100%); color: white; padding: 20px; border-radius: 12px; text-align: center; }
    .stat-value { font-size: 32px; font-weight: 700; margin-bottom: 5px; }
    .stat-label { font-size: 12px; opacity: 0.8; }
  </style>
</head>
<body>
  <div class="header">
    <div class="header-title">🏛️ 메타도어 관리자</div>
    <button class="logout-btn" onclick="logout()">로그아웃</button>
  </div>
  
  <div class="container">
    <div class="menu-tabs">
      <button class="menu-tab active" onclick="switchTab('field')">현장점검</button>
      <button class="menu-tab" onclick="switchTab('remote')">원격점검</button>
      <button class="menu-tab" onclick="switchTab('report')">점검보고서</button>
      <button class="menu-tab" onclick="switchTab('member')">회원관리</button>
    </div>
    
    <!-- 현장점검 -->
    <div id="field" class="content">
      <h2 style="margin-bottom: 16px;">현장점검</h2>
      <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; margin-bottom: 20px;">
        <div>
          <label style="display: block; font-size: 12px; font-weight: 600; margin-bottom: 8px;">구 선택</label>
          <select id="field-district" onchange="loadFieldLocations()" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 6px;">
            <option value="">-- 선택하세요 --</option>
          </select>
        </div>
        <div>
          <label style="display: block; font-size: 12px; font-weight: 600; margin-bottom: 8px;">월 선택</label>
          <select id="field-month" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 6px;">
            <option value="">-- 선택하세요 --</option>
          </select>
        </div>
        <div style="display: flex; align-items: flex-end;">
          <button onclick="filterFieldData()" style="width: 100%; padding: 8px; background: #1e5a96; color: white; border: none; border-radius: 6px; cursor: pointer;">검색</button>
        </div>
      </div>
      
      <table class="table">
        <thead>
          <tr>
            <th>구</th>
            <th>설치 위치</th>
            <th>상태</th>
            <th>조치 내용</th>
            <th>작업</th>
          </tr>
        </thead>
        <tbody id="field-table">
          <tr><td colspan="5" style="text-align: center; color: #999;">데이터를 선택해주세요</td></tr>
        </tbody>
      </table>
    </div>
    
    <!-- 원격점검 -->
    <div id="remote" class="content hidden">
      <h2 style="margin-bottom: 16px;">원격점검</h2>
      <div style="display: grid; grid-template-columns: 200px 1fr; gap: 20px;">
        <div style="border-right: 1px solid #ddd; padding-right: 20px;">
          <label style="display: block; font-size: 12px; font-weight: 600; margin-bottom: 8px;">구</label>
          <select id="remote-district" onchange="loadRemoteLocations()" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 6px; margin-bottom: 16px;">
            <option value="">-- 선택하세요 --</option>
          </select>
          <div id="remote-location-list" style="max-height: 400px; overflow-y: auto;"></div>
        </div>
        <div>
          <label style="display: block; font-size: 12px; font-weight: 600; margin-bottom: 8px;">점검 항목</label>
          <div id="remote-item-list" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 20px;"></div>
          
          <label style="display: block; font-size: 12px; font-weight: 600; margin-bottom: 8px;">월별 상태</label>
          <div id="remote-month-grid" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px;"></div>
        </div>
      </div>
    </div>
    
    <!-- 점검보고서 -->
    <div id="report" class="content hidden">
      <h2 style="margin-bottom: 16px;">점검보고서</h2>
      <p style="color: #666;">점검 통계 및 보고서 기능</p>
    </div>
    
    <!-- 회원관리 -->
    <div id="member" class="content hidden">
      <h2 style="margin-bottom: 16px;">회원관리</h2>
      <table class="table">
        <thead>
          <tr>
            <th>사용자명</th>
            <th>역할</th>
            <th>가입일</th>
            <th>상태</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>admin</td>
            <td>관리자</td>
            <td>2024-05-01</td>
            <td><span style="color: #4caf50;">활성</span></td>
          </tr>
          <tr>
            <td>user</td>
            <td>점검원</td>
            <td>2024-05-05</td>
            <td><span style="color: #4caf50;">활성</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
  
  <script>
    const METADOOR_DATA = ''' + json.dumps(METADOOR_DATA, ensure_ascii=False) + ''';
    const INSPECTION_ITEMS = ''' + json.dumps(INSPECTION_ITEMS, ensure_ascii=False) + ''';
    
    function initAdmin() {
      // 구 선택 옵션 추가
      const districtSelect = document.getElementById('field-district');
      const remoteDistrictSelect = document.getElementById('remote-district');
      
      Object.keys(METADOOR_DATA).forEach(district => {
        const option = document.createElement('option');
        option.value = district;
        option.textContent = district;
        districtSelect.appendChild(option.cloneNode(true));
        remoteDistrictSelect.appendChild(option.cloneNode(true));
      });
      
      // 월 선택 옵션 추가
      const monthSelect = document.getElementById('field-month');
      for (let i = 1; i <= 12; i++) {
        const option = document.createElement('option');
        option.value = i;
        option.textContent = i + '월';
        monthSelect.appendChild(option);
      }
      
      // 점검 항목 버튼 생성
      const itemList = document.getElementById('remote-item-list');
      INSPECTION_ITEMS.forEach(item => {
        const btn = document.createElement('button');
        btn.textContent = item;
        btn.style.cssText = 'padding: 8px; background: #f0f0f0; border: 1px solid #ddd; border-radius: 6px; cursor: pointer;';
        btn.onclick = () => selectRemoteItem(item, btn);
        itemList.appendChild(btn);
      });
      
      // 월별 그리드 생성
      const monthGrid = document.getElementById('remote-month-grid');
      for (let i = 1; i <= 12; i++) {
        const btn = document.createElement('button');
        btn.textContent = i + '월';
        btn.style.cssText = 'padding: 8px; background: #f0f0f0; border: 1px solid #ddd; border-radius: 6px; cursor: pointer;';
        btn.onclick = () => toggleRemoteMonth(i, btn);
        monthGrid.appendChild(btn);
      }
    }
    
    function switchTab(tab) {
      document.querySelectorAll('.content').forEach(c => c.classList.add('hidden'));
      document.getElementById(tab).classList.remove('hidden');
      document.querySelectorAll('.menu-tab').forEach(t => t.classList.remove('active'));
      event.target.classList.add('active');
    }
    
    function loadFieldLocations() {
      const district = document.getElementById('field-district').value;
      const table = document.getElementById('field-table');
      if (!district) {
        table.innerHTML = '<tr><td colspan="5" style="text-align: center; color: #999;">구를 선택하세요</td></tr>';
        return;
      }
      
      const html = METADOOR_DATA[district].map(location => `
        <tr>
          <td>${district}</td>
          <td>${location}</td>
          <td><span style="color: #4caf50;">정상</span></td>
          <td>-</td>
          <td><button onclick="viewDetails('${district}', '${location}')" style="padding: 4px 8px; background: #1e5a96; color: white; border: none; border-radius: 4px; cursor: pointer;">보기</button></td>
        </tr>
      `).join('');
      table.innerHTML = html;
    }
    
    function loadRemoteLocations() {
      const district = document.getElementById('remote-district').value;
      const locList = document.getElementById('remote-location-list');
      if (!district) {
        locList.innerHTML = '<p style="color: #999;">구를 선택하세요</p>';
        return;
      }
      
      const html = METADOOR_DATA[district].map(location => `
        <div style="padding: 8px; background: #f9f9f9; border: 1px solid #ddd; border-radius: 6px; margin-bottom: 8px; cursor: pointer;" onclick="selectRemoteLocation('${location}')">${location}</div>
      `).join('');
      locList.innerHTML = html;
    }
    
    function selectRemoteItem(item, btn) {
      btn.style.background = btn.style.background === 'rgb(30, 90, 150)' ? '#f0f0f0' : '#1e5a96';
      btn.style.color = btn.style.background === 'rgb(30, 90, 150)' ? 'white' : 'black';
    }
    
    function selectRemoteLocation(location) {
      alert(location + ' 선택됨');
    }
    
    function toggleRemoteMonth(month, btn) {
      btn.style.background = btn.style.background === 'rgb(30, 90, 150)' ? '#f0f0f0' : '#1e5a96';
      btn.style.color = btn.style.background === 'rgb(30, 90, 150)' ? 'white' : 'black';
    }
    
    function filterFieldData() {
      loadFieldLocations();
    }
    
    function viewDetails(district, location) {
      alert(district + ' - ' + location + '의 상세 내용');
    }
    
    function logout() {
      window.location.href = '/logout';
    }
    
    initAdmin();
  </script>
</body>
</html>
'''

# ===== 라우트 =====
@app.route('/')
def index():
    if 'logged_in' not in session:
        return render_template_string(USER_APP_HTML)
    return redirect('/app')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if data['username'] == USER_USERNAME and data['password'] == USER_PASSWORD:
        session['logged_in'] = True
        session['role'] = 'user'
        return jsonify({'success': True})
    return jsonify({'success': False}), 401

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/')

@app.route('/app/inspection')
def app_inspection():
    if 'logged_in' not in session:
        return redirect('/')
    return render_template_string(USER_APP_HTML)

@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    if data['username'] == ADMIN_USERNAME and data['password'] == ADMIN_PASSWORD:
        session['logged_in'] = True
        session['role'] = 'admin'
        return jsonify({'success': True})
    return jsonify({'success': False}), 401

@app.route('/admin')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect('/admin-login')
    return render_template_string(ADMIN_DASHBOARD_HTML)

@app.route('/admin-login')
def admin_login_page():
    return '''
    <!DOCTYPE html>
    <html lang="ko">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>메타도어 관리자 로그인</title>
      <style>
        body { font-family: -apple-system, sans-serif; background: linear-gradient(135deg, #1e5a96 0%, #164a7a 100%); min-height: 100vh; display: flex; justify-content: center; align-items: center; }
        .card { background: white; padding: 40px; border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); width: 100%; max-width: 400px; text-align: center; }
        .logo { font-size: 56px; margin-bottom: 16px; }
        .title { font-size: 28px; font-weight: 700; margin-bottom: 8px; }
        .subtitle { font-size: 14px; color: #999; margin-bottom: 32px; }
        .form-group { margin-bottom: 20px; text-align: left; }
        .label { display: block; font-size: 13px; font-weight: 600; margin-bottom: 8px; }
        input { width: 100%; padding: 11px 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; }
        input:focus { outline: none; border-color: #1e5a96; }
        .btn { width: 100%; padding: 12px; background: #1e5a96; color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: 700; cursor: pointer; margin-top: 16px; }
        .btn:hover { background: #164a7a; }
      </style>
    </head>
    <body>
      <div class="card">
        <div class="logo">🏛️</div>
        <div class="title">메타도어</div>
        <div class="subtitle">관리자 로그인</div>
        <form onsubmit="handleAdminLogin(event)">
          <div class="form-group">
            <label class="label">아이디</label>
            <input type="text" id="username" value="admin" required>
          </div>
          <div class="form-group">
            <label class="label">비밀번호</label>
            <input type="password" id="password" value="admin123" required>
          </div>
          <button type="submit" class="btn">로그인</button>
        </form>
      </div>
      
      <script>
        function handleAdminLogin(e) {
          e.preventDefault();
          fetch('/admin/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              username: document.getElementById('username').value,
              password: document.getElementById('password').value
            })
          }).then(r => r.json()).then(data => {
            if (data.success) window.location.href = '/admin';
            else alert('로그인 실패');
          });
        }
      </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
