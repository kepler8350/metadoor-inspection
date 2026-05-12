import os
import json
from flask import Flask, render_template_string, request, session, jsonify, redirect
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'metadoor-secret-key-2024'
DB_PATH = '/tmp/metadoor.db'

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

# 메타도어 설치 데이터 - 정확한 정보
METADOOR_DATA = {
    '금정구': [
        {'name': '금정종로금융', 'address': '부산시 금정구 부곡동'},
        {'name': '금정구청', 'address': '부산시 금정구 중앙로'},
        {'name': '금정도서관', 'address': '부산시 금정구 장전로'}
    ],
    '기장군': [
        {'name': '기장읍행정복합', 'address': '부산시 기장군 기장읍'},
        {'name': '기장도서관', 'address': '부산시 기장군 정관면'},
        {'name': '정관중학교', 'address': '부산시 기장군 정관면'}
    ],
    '남구': [
        {'name': '남구청', 'address': '부산시 남구 수로왕대로'},
        {'name': '용호문화센터', 'address': '부산시 남구 용호동'},
        {'name': '남부경찰서', 'address': '부산시 남구 가야로'}
    ],
    '동구': [
        {'name': '동구청', 'address': '부산시 동구 중앙대로'},
        {'name': '초량문화센터', 'address': '부산시 동구 초량동'},
        {'name': '범일도서관', 'address': '부산시 동구 범일로'}
    ],
    '동래구': [
        {'name': '동래구청', 'address': '부산시 동래구 명륜로'},
        {'name': '동래도서관', 'address': '부산시 동래구 온천장로'},
        {'name': '명장문화센터', 'address': '부산시 동래구 온천동'}
    ],
    '부산진구': [
        {'name': '부산진구청', 'address': '부산시 부산진구 중앙대로'},
        {'name': '부산진도서관', 'address': '부산시 부산진구 서면로'},
        {'name': '서면문화센터', 'address': '부산시 부산진구 동성로'}
    ],
    '북구': [
        {'name': '북구청', 'address': '부산시 북구 만평동'},
        {'name': '북부도서관', 'address': '부산시 북구 낙동대로'},
        {'name': '구포문화센터', 'address': '부산시 북구 구포동'}
    ],
    '사상구': [
        {'name': '사상구청', 'address': '부산시 사상구 사상로'},
        {'name': '사상도서관', 'address': '부산시 사상구 모라로'},
        {'name': '삼락도서관', 'address': '부산시 사상구 삼락동'}
    ],
    '사하구': [
        {'name': '사하구청', 'address': '부산시 사하구 을숙도대로'},
        {'name': '사하도서관', 'address': '부산시 사하구 신평로'},
        {'name': '감천문화마을센터', 'address': '부산시 사하구 감내로'}
    ],
    '서구': [
        {'name': '서구청', 'address': '부산시 서구 서감로'},
        {'name': '서도서관', 'address': '부산시 서구 구덕로'},
        {'name': '부산관광공사', 'address': '부산시 서구 해변로'}
    ],
    '수영구': [
        {'name': '수영구청', 'address': '부산시 수영구 남천로'},
        {'name': '수영도서관', 'address': '부산시 수영구 수영로'},
        {'name': '광안리해수욕장관리사무소', 'address': '부산시 수영구 광안리로'}
    ],
    '연제구': [
        {'name': '연제구청', 'address': '부산시 연제구 중앙로'},
        {'name': '연제도서관', 'address': '부산시 연제구 거제로'},
        {'name': '연제문화센터', 'address': '부산시 연제구 중앙대로'}
    ],
    '영도구': [
        {'name': '영도구청', 'address': '부산시 영도구 영도대로'},
        {'name': '영도도서관', 'address': '부산시 영도구 절영로'},
        {'name': '절영로역사관', 'address': '부산시 영도구 봉래로'}
    ],
    '중구': [
        {'name': '중구청', 'address': '부산시 중구 중앙대로'},
        {'name': '중앙도서관', 'address': '부산시 중구 중앙대로'},
        {'name': '부산항만공사', 'address': '부산시 중구 신항로'}
    ],
    '해운대구': [
        {'name': '해운대구청', 'address': '부산시 해운대구 중앙대로'},
        {'name': '해운대도서관', 'address': '부산시 해운대구 해운대로'},
        {'name': '해운대해수욕장관리사무소', 'address': '부산시 해운대구 우동'}
    ]
}

# 점검 항목 - 정확한 정보
INSPECTION_ITEMS = [
    '패널',
    '보드',
    '전원',
    'PC',
    '카메라',
    '스피커',
    '마이크',
    '입력장치',
    '하우징',
    '외관데코',
    '기타'
]

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inspections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            district TEXT NOT NULL,
            location TEXT NOT NULL,
            item TEXT NOT NULL,
            content TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect('/admin/login')
        return f(*args, **kwargs)
    return decorated_function

# 모바일 앱 HTML
MOBILE_APP_HTML = '''
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>메타도어 점검 앱</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: #f5f7fa;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      padding: 10px;
    }
    .mobile-frame {
      width: 100%;
      max-width: 375px;
      height: 812px;
      background: white;
      border-radius: 40px;
      border: 12px solid #000;
      box-shadow: 0 20px 60px rgba(0,0,0,0.3);
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }
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
    input { width: 100%; padding: 11px 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; font-family: inherit; background: #fafafa; }
    input:focus { outline: none; border-color: #1e5a96; background: white; }
    .btn { width: 100%; padding: 12px; border: none; border-radius: 8px; font-size: 15px; font-weight: 700; cursor: pointer; transition: all 0.2s; font-family: inherit; }
    .btn-primary { background: #1e5a96; color: white; margin-top: 4px; }
    .btn-primary:active { background: #164a7a; }
    .help-text { font-size: 11px; color: #999; text-align: center; margin-top: 12px; }
    
    .district-screen { flex-direction: row; }
    .header { background: #1e5a96; color: white; padding: 12px 16px; font-size: 18px; font-weight: 700; }
    .content-area { flex: 1; display: flex; overflow: hidden; }
    .left-panel { width: 40%; background: #f5f7fa; border-right: 1px solid #eee; overflow-y: auto; padding: 8px; }
    .right-panel { width: 60%; background: white; overflow-y: auto; padding: 12px 16px; }
    .district-btn { width: 100%; padding: 10px 12px; background: white; border: 1px solid #ddd; border-radius: 6px; font-size: 13px; font-weight: 500; color: #333; cursor: pointer; margin-bottom: 4px; text-align: left; font-family: inherit; }
    .district-btn.selected { background: #1e5a96; color: white; border-color: #1e5a96; }
    .location-list { display: none; }
    .location-list.active { display: block; }
    .location-item { padding: 11px; background: white; border-radius: 6px; margin-bottom: 8px; border: 1px solid #eee; cursor: pointer; font-size: 13px; color: #333; }
    .location-item:active { background: #f0f0f0; }
    .location-name { font-weight: 600; margin-bottom: 3px; }
    .location-address { font-size: 11px; color: #999; }
    
    .inspection-screen { padding: 16px; overflow-y: auto; }
    .inspection-info { background: #1e5a96; color: white; padding: 14px; border-radius: 10px; margin-bottom: 14px; text-align: center; }
    .inspection-name { font-size: 16px; font-weight: 700; margin-bottom: 3px; }
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
      <!-- 로그인 화면 -->
      <div class="screen login-screen active">
        <div class="login-container">
          <div class="logo">🏛️</div>
          <div class="title">메타도어</div>
          <div class="subtitle">유지보수 점검 시스템</div>
          <div class="login-card">
            <div class="input-group">
              <label class="label">아이디</label>
              <input type="text" id="username" value="admin" placeholder="아이디">
            </div>
            <div class="input-group">
              <label class="label">비밀번호</label>
              <input type="password" id="password" value="admin123" placeholder="비밀번호">
            </div>
            <button class="btn btn-primary" onclick="handleLogin()">로그인</button>
            <div class="help-text">권한자가 등록한<br>직원만 로그인 가능합니다.</div>
          </div>
        </div>
      </div>
      
      <!-- 구 선택 화면 -->
      <div class="screen district-screen">
        <div class="header">구 선택</div>
        <div class="content-area">
          <div class="left-panel">
            <div class="district-list" id="district-list"></div>
          </div>
          <div class="right-panel">
            <div id="location-lists"></div>
            <div style="text-align: center; padding: 40px 16px; color: #999;">왼쪽에서 구를 선택하세요</div>
          </div>
        </div>
      </div>
      
      <!-- 점검 화면 -->
      <div class="screen inspection-screen">
        <div class="inspection-info">
          <div class="inspection-name" id="insp-name">사상구 - 사상구청</div>
          <div style="font-size: 11px; color: rgba(255, 255, 255, 0.7);">점검 입력 / 3단계</div>
        </div>
        <div class="form-group">
          <div class="form-title">점검 항목</div>
          <select id="insp-type">
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
            <option value="요주의">! 요주의</option>
            <option value="이상">✕ 이상</option>
          </select>
        </div>
        <div class="button-group">
          <button class="btn btn-secondary" onclick="handleSave()">임시 저장</button>
          <button class="btn btn-primary" onclick="handleSubmit()">완료</button>
        </div>
      </div>
    </div>
  </div>
  
  <script>
    const metadoorData = METADOOR_DATA;
    const inspectionItems = INSPECTION_ITEMS;
    
    function initDistricts() {
      const districtList = document.getElementById('district-list');
      const locationLists = document.getElementById('location-lists');
      
      Object.keys(metadoorData).forEach(district => {
        const btn = document.createElement('button');
        btn.className = 'district-btn';
        btn.textContent = district;
        btn.onclick = function() { selectDistrict(district, this); };
        districtList.appendChild(btn);
        
        const listDiv = document.createElement('div');
        listDiv.className = 'location-list';
        listDiv.id = 'list-' + district;
        
        metadoorData[district].forEach(location => {
          const item = document.createElement('div');
          item.className = 'location-item';
          item.innerHTML = '<div class="location-name">' + location.name + '</div><div class="location-address">' + location.address + '</div>';
          item.onclick = function() { selectLocation(district, location); };
          listDiv.appendChild(item);
        });
        
        locationLists.appendChild(listDiv);
      });
      
      const typeSelect = document.getElementById('insp-type');
      inspectionItems.forEach((item, idx) => {
        const option = document.createElement('option');
        option.value = item;
        option.textContent = item;
        typeSelect.appendChild(option);
      });
    }
    
    function handleLogin() {
      const username = document.getElementById('username').value;
      const password = document.getElementById('password').value;
      if (username === 'admin' && password === 'admin123') {
        showScreen(1);
      } else {
        alert('아이디 또는 비밀번호가 올바르지 않습니다.');
      }
    }
    
    function selectDistrict(district, btn) {
      document.querySelectorAll('.district-btn').forEach(b => b.classList.remove('selected'));
      btn.classList.add('selected');
      document.querySelectorAll('.location-list').forEach(l => l.classList.remove('active'));
      document.getElementById('list-' + district).classList.add('active');
    }
    
    function selectLocation(district, location) {
      document.getElementById('insp-name').textContent = district + ' - ' + location.name;
      window.currentDistrict = district;
      window.currentLocation = location.name;
      showScreen(2);
    }
    
    function showScreen(index) {
      document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
      document.querySelectorAll('.screen')[index].classList.add('active');
    }
    
    function handleSave() {
      alert('임시 저장되었습니다.');
    }
    
    function handleSubmit() {
      const type = document.getElementById('insp-type').value;
      if (!type) {
        alert('점검 항목을 선택하세요.');
        return;
      }
      
      const data = {
        district: window.currentDistrict,
        location: window.currentLocation,
        item: type,
        content: document.getElementById('insp-content').value,
        status: document.getElementById('insp-status').value
      };
      
      fetch('/api/inspection', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      }).then(r => r.json()).then(res => {
        alert('점검이 완료되었습니다!');
        showScreen(1);
      });
    }
    
    initDistricts();
  </script>
  <script>
    const METADOOR_DATA = ''' + json.dumps(METADOOR_DATA) + ''';
    const INSPECTION_ITEMS = ''' + json.dumps(INSPECTION_ITEMS) + ''';
  </script>
</body>
</html>
'''

# 관리자 대시보드 HTML
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
    
    .header { background: linear-gradient(135deg, #1e5a96 0%, #164a7a 100%); color: white; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center; }
    .header-title { font-size: 24px; font-weight: 700; }
    .logout-btn { background: rgba(255,255,255,0.2); border: 1px solid rgba(255,255,255,0.3); color: white; padding: 8px 16px; border-radius: 6px; cursor: pointer; }
    
    .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
    
    .dashboard-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
    .stat-card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
    .stat-label { font-size: 14px; color: #999; margin-bottom: 8px; }
    .stat-value { font-size: 32px; font-weight: 700; color: #1e5a96; }
    
    .table-container { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); overflow-x: auto; }
    .table { width: 100%; border-collapse: collapse; }
    .table thead { background: #f9f9f9; }
    .table th { padding: 12px; text-align: left; font-weight: 600; color: #333; border-bottom: 1px solid #eee; }
    .table td { padding: 12px; border-bottom: 1px solid #eee; color: #666; }
    .table tr:hover { background: #fafafa; }
    
    .status-normal { color: #4caf50; font-weight: 600; }
    .status-warning { color: #ff9800; font-weight: 600; }
    .status-error { color: #f44336; font-weight: 600; }
  </style>
</head>
<body>
  <div class="header">
    <div class="header-title">🏛️ 메타도어 관리자</div>
    <button class="logout-btn" onclick="logout()">로그아웃</button>
  </div>
  
  <div class="container">
    <div class="dashboard-grid">
      <div class="stat-card">
        <div class="stat-label">총 점검 수</div>
        <div class="stat-value" id="total-inspections">0</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">정상</div>
        <div class="stat-value" style="color: #4caf50;" id="normal-count">0</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">요주의</div>
        <div class="stat-value" style="color: #ff9800;" id="warning-count">0</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">이상</div>
        <div class="stat-value" style="color: #f44336;" id="error-count">0</div>
      </div>
    </div>
    
    <div class="table-container">
      <h2 style="margin-bottom: 16px;">점검 기록</h2>
      <table class="table">
        <thead>
          <tr>
            <th>구</th>
            <th>설치 위치</th>
            <th>점검 항목</th>
            <th>점검 상태</th>
            <th>조사 내용</th>
            <th>등록일</th>
          </tr>
        </thead>
        <tbody id="inspections-table">
          <tr><td colspan="6" style="text-align: center; color: #999;">점검 기록이 없습니다.</td></tr>
        </tbody>
      </table>
    </div>
  </div>
  
  <script>
    function loadInspections() {
      fetch('/api/inspections')
        .then(r => r.json())
        .then(data => {
          const tbody = document.getElementById('inspections-table');
          tbody.innerHTML = '';
          
          let normal = 0, warning = 0, error = 0;
          
          data.forEach(insp => {
            const row = document.createElement('tr');
            let statusClass = 'status-normal';
            if (insp.status === '요주의') { statusClass = 'status-warning'; warning++; }
            else if (insp.status === '이상') { statusClass = 'status-error'; error++; }
            else { normal++; }
            
            const date = new Date(insp.created_at).toLocaleDateString('ko-KR');
            row.innerHTML = \`
              <td>\${insp.district}</td>
              <td>\${insp.location}</td>
              <td>\${insp.item}</td>
              <td><span class="\${statusClass}">\${insp.status}</span></td>
              <td>\${insp.content || '-'}</td>
              <td>\${date}</td>
            \`;
            tbody.appendChild(row);
          });
          
          document.getElementById('total-inspections').textContent = data.length;
          document.getElementById('normal-count').textContent = normal;
          document.getElementById('warning-count').textContent = warning;
          document.getElementById('error-count').textContent = error;
        });
    }
    
    function logout() {
      fetch('/admin/logout', { method: 'POST' }).then(() => {
        window.location.href = '/admin/login';
      });
    }
    
    loadInspections();
    setInterval(loadInspections, 5000);
  </script>
</body>
</html>
'''

# 관리자 로그인 페이지
ADMIN_LOGIN_HTML = '''
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>메타도어 - 관리자 로그인</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: linear-gradient(135deg, #1e5a96 0%, #164a7a 100%);
      min-height: 100vh;
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 20px;
    }
    .login-card {
      background: white;
      border-radius: 16px;
      padding: 40px;
      box-shadow: 0 10px 40px rgba(0,0,0,0.2);
      width: 100%;
      max-width: 400px;
      text-align: center;
    }
    .logo { font-size: 56px; margin-bottom: 16px; }
    .title { font-size: 28px; font-weight: 700; color: #333; margin-bottom: 8px; }
    .subtitle { font-size: 14px; color: #999; margin-bottom: 32px; }
    .form-group { margin-bottom: 20px; text-align: left; }
    .label { display: block; font-size: 13px; font-weight: 600; color: #333; margin-bottom: 8px; }
    input {
      width: 100%;
      padding: 11px 12px;
      border: 1px solid #ddd;
      border-radius: 8px;
      font-size: 14px;
      font-family: inherit;
    }
    input:focus { outline: none; border-color: #1e5a96; }
    .btn {
      width: 100%;
      padding: 12px;
      background: #1e5a96;
      color: white;
      border: none;
      border-radius: 8px;
      font-size: 16px;
      font-weight: 700;
      cursor: pointer;
      margin-top: 16px;
    }
    .btn:hover { background: #164a7a; }
  </style>
</head>
<body>
  <div class="login-card">
    <div class="logo">🏛️</div>
    <div class="title">메타도어</div>
    <div class="subtitle">관리자 페이지</div>
    <form onsubmit="handleLogin(event)">
      <div class="form-group">
        <label class="label">아이디</label>
        <input type="text" id="username" placeholder="아이디" required>
      </div>
      <div class="form-group">
        <label class="label">비밀번호</label>
        <input type="password" id="password" placeholder="비밀번호" required>
      </div>
      <button type="submit" class="btn">로그인</button>
    </form>
  </div>
  
  <script>
    function handleLogin(e) {
      e.preventDefault();
      const username = document.getElementById('username').value;
      const password = document.getElementById('password').value;
      
      fetch('/admin/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      }).then(r => r.json()).then(data => {
        if (data.success) {
          window.location.href = '/admin';
        } else {
          alert('아이디 또는 비밀번호가 올바르지 않습니다.');
        }
      });
    }
  </script>
</body>
</html>
'''

# 라우트
@app.route('/')
def index():
    return render_template_string(MOBILE_APP_HTML)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        data = request.json
        if data['username'] == ADMIN_USERNAME and data['password'] == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return jsonify({'success': True})
        return jsonify({'success': False}), 401
    return render_template_string(ADMIN_LOGIN_HTML)

@app.route('/admin')
@login_required
def admin_dashboard():
    return render_template_string(ADMIN_DASHBOARD_HTML)

@app.route('/admin/logout', methods=['POST'])
def admin_logout():
    session.pop('admin_logged_in', None)
    return jsonify({'success': True})

@app.route('/api/inspection', methods=['POST'])
def save_inspection():
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO inspections (district, location, item, content, status, user)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (data['district'], data['location'], data['item'], data['content'], data['status'], 'user'))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/inspections')
@login_required
def get_inspections():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM inspections ORDER BY created_at DESC')
    inspections = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(inspections)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
