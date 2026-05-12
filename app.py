import os
from flask import Flask, request, session, redirect
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'metadoor-key-2024'

DB_PATH = '/tmp/metadoor.db'

def get_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT)')
        c.execute('CREATE TABLE inspections (id INTEGER PRIMARY KEY, user_id INTEGER, location TEXT, items TEXT, completed_at TIMESTAMP)')
        c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                 ('admin', generate_password_hash('admin123'), 'admin'))
        conn.commit()
        conn.close()
    return sqlite3.connect(DB_PATH)

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/dashboard')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        try:
            conn = get_db()
            c = conn.cursor()
            c.execute('SELECT id, username, role, password FROM users WHERE username = ?', (username,))
            user = c.fetchone()
            conn.close()
            
            if user and check_password_hash(user[3], password):
                session['user_id'] = user[0]
                session['username'] = user[1]
                session['role'] = user[2]
                return redirect('/dashboard')
            else:
                error = '로그인 실패'
        except Exception as e:
            error = f'오류: {str(e)}'
    
    return f'''
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>메타도어 - 로그인</title>
        <style>
            body {{ font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; justify-content: center; align-items: center; }}
            .container {{ background: white; padding: 40px; border-radius: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.3); width: 100%; max-width: 400px; }}
            h1 {{ text-align: center; color: #333; }}
            .form-group {{ margin: 20px 0; }}
            label {{ display: block; margin-bottom: 5px; font-weight: bold; }}
            input {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
            button {{ width: 100%; padding: 10px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }}
            .error {{ color: red; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏛️ 메타도어</h1>
            {f'<div class="error">{error}</div>' if error else ''}
            <form method="POST">
                <div class="form-group">
                    <label>사용자명</label>
                    <input type="text" name="username" required>
                </div>
                <div class="form-group">
                    <label>비밀번호</label>
                    <input type="password" name="password" required>
                </div>
                <button type="submit">로그인</button>
            </form>
            <p style="text-align: center; margin-top: 20px;">테스트: admin / admin123</p>
        </div>
    </body>
    </html>
    '''

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM inspections WHERE user_id = ?', (session['user_id'],))
        count = c.fetchone()[0]
        conn.close()
    except:
        count = 0
    
    return f'''
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>메타도어 - 대시보드</title>
        <style>
            body {{ font-family: Arial; background: #f5f5f5; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; display: flex; justify-content: space-between; }}
            .container {{ max-width: 1200px; margin: 30px auto; padding: 0 20px; }}
            .card {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin: 20px 0; }}
            a {{ color: white; text-decoration: none; background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🏛️ 메타도어</h1>
            <div>
                <span style="margin-right: 20px;">{session.get('username', 'user')}님 환영합니다!</span>
                <a href="/logout">로그아웃</a>
            </div>
        </div>
        
        <div class="container">
            <div class="card">
                <h2>점검 통계</h2>
                <p>총 점검 횟수: {count}</p>
            </div>
            <div class="card">
                <a href="/inspection" style="display: inline-block;">✏️ 새 점검 입력</a>
                <a href="/logout" style="display: inline-block; margin-left: 10px;">로그아웃</a>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/inspection', methods=['GET', 'POST'])
def inspection():
    if 'user_id' not in session:
        return redirect('/login')
    
    if request.method == 'POST':
        location = request.form.get('location')
        conn = get_db()
        c = conn.cursor()
        c.execute('INSERT INTO inspections (user_id, location, items, completed_at) VALUES (?, ?, ?, ?)',
                 (session['user_id'], location, '[]', datetime.now()))
        conn.commit()
        conn.close()
        return redirect('/inspection-complete')
    
    districts = ['강서구', '사상구', '동구', '영도구', '남구', '중구', '서구', '부산진구', 
                '동래구', '남동구', '북구', '해운대구', '수영구', '연제구', '금정구']
    options = ''.join([f'<option value="{d}">{d}</option>' for d in districts])
    
    return f'''
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>메타도어 - 점검 입력</title>
        <style>
            body {{ font-family: Arial; background: #f5f5f5; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; display: flex; justify-content: space-between; }}
            .container {{ max-width: 800px; margin: 30px auto; padding: 0 20px; }}
            .card {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            select {{ width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
            button {{ width: 100%; padding: 10px; background: #27ae60; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; margin-top: 20px; }}
            a {{ color: white; text-decoration: none; background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🏛️ 메타도어</h1>
            <a href="/dashboard">← 대시보드</a>
        </div>
        
        <div class="container">
            <div class="card">
                <h2>유지보수 점검</h2>
                <form method="POST">
                    <label>점검 위치</label>
                    <select name="location" required>
                        <option value="">선택하세요</option>
                        {options}
                    </select>
                    <button type="submit">점검 완료</button>
                </form>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/inspection-complete')
def inspection_complete():
    return '''
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>메타도어 - 완료</title>
        <style>
            body {{ font-family: Arial; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; justify-content: center; align-items: center; }}
            .container {{ background: white; padding: 60px 40px; border-radius: 15px; box-shadow: 0 10px 40px rgba(0,0,0,0.3); text-align: center; max-width: 500px; }}
            h1 {{ color: #27ae60; }}
            a {{ display: inline-block; padding: 10px 20px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✓ 점검이 완료되었습니다!</h1>
            <p>점검 기록이 저장되었습니다.</p>
            <a href="/dashboard">대시보드로 돌아가기</a>
            <a href="/inspection">다음 점검</a>
        </div>
    </body>
    </html>
    '''

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/mobile')
def mobile():
    """모바일 앱 인터페이스"""
    return '''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <title>메타도어 - 모바일 점검 앱</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: #f5f5f5;
            color: #333;
        }

        .mobile-container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 0 30px rgba(0, 0, 0, 0.1);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        .status-bar {
            background: #000;
            color: white;
            padding: 8px 16px;
            font-size: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            height: 24px;
        }

        .header {
            background: linear-gradient(135deg, #1e5a96 0%, #164a7a 100%);
            color: white;
            padding: 20px 16px;
        }

        .header-title {
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 4px;
        }

        .header-subtitle {
            font-size: 13px;
            opacity: 0.85;
        }

        .page {
            display: none;
            flex: 1;
            overflow-y: auto;
            -webkit-overflow-scrolling: touch;
        }

        .page.active {
            display: flex;
            flex-direction: column;
        }

        .page-content {
            flex: 1;
            padding: 16px;
        }

        #loginPage {
            background: linear-gradient(135deg, #1e5a96 0%, #164a7a 100%);
        }

        .login-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 24px;
        }

        .logo {
            font-size: 48px;
            margin-bottom: 12px;
        }

        .app-title {
            font-size: 28px;
            font-weight: 700;
            color: white;
            margin-bottom: 8px;
        }

        .app-subtitle {
            font-size: 14px;
            color: rgba(255, 255, 255, 0.8);
            margin-bottom: 32px;
        }

        .login-card {
            background: white;
            border-radius: 20px;
            padding: 32px 24px;
            width: 100%;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-label {
            display: block;
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 8px;
            color: #333;
        }

        .form-input {
            width: 100%;
            padding: 12px 14px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            font-family: inherit;
        }

        .form-input:focus {
            outline: none;
            border-color: #1e5a96;
            box-shadow: 0 0 0 3px rgba(30, 90, 150, 0.1);
        }

        .btn {
            width: 100%;
            padding: 12px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            font-family: inherit;
        }

        .btn-primary {
            background: #1e5a96;
            color: white;
            margin-top: 8px;
        }

        .btn-primary:active {
            background: #164a7a;
            transform: scale(0.98);
        }

        .login-help {
            font-size: 12px;
            color: #999;
            text-align: center;
            margin-top: 16px;
        }

        .district-list {
            display: grid;
            gap: 8px;
        }

        .district-btn {
            padding: 14px 16px;
            border: 1px solid #ddd;
            border-radius: 8px;
            background: white;
            font-size: 15px;
            cursor: pointer;
            transition: all 0.2s;
            text-align: left;
        }

        .district-btn:active {
            background: #f0f0f0;
            transform: scale(0.98);
        }

        .district-btn.selected {
            background: #1e5a96;
            color: white;
            border-color: #1e5a96;
        }

        .inspection-form {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        .form-section {
            padding: 16px;
            background: #f9f9f9;
            border-radius: 8px;
        }

        .form-section-title {
            font-size: 13px;
            font-weight: 600;
            color: #666;
            margin-bottom: 12px;
            text-transform: uppercase;
        }

        .select-input, .textarea-input {
            width: 100%;
            padding: 12px 14px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            font-family: inherit;
            background: white;
        }

        .textarea-input {
            min-height: 100px;
            resize: vertical;
        }

        .textarea-input:focus, .select-input:focus {
            outline: none;
            border-color: #1e5a96;
            box-shadow: 0 0 0 3px rgba(30, 90, 150, 0.1);
        }

        .image-upload {
            border: 2px dashed #ddd;
            border-radius: 8px;
            padding: 16px;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s;
        }

        .image-upload:hover {
            border-color: #1e5a96;
            background: rgba(30, 90, 150, 0.05);
        }

        .image-upload-icon {
            font-size: 32px;
            margin-bottom: 8px;
        }

        .image-upload-text {
            font-size: 13px;
            color: #999;
        }

        #imageInput {
            display: none;
        }

        .image-preview {
            margin-top: 12px;
            border-radius: 8px;
            max-width: 100%;
            max-height: 200px;
        }

        .button-group {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            margin-top: 8px;
        }

        .btn-secondary {
            background: #e0e0e0;
            color: #333;
        }

        .btn-secondary:active {
            background: #d0d0d0;
        }

        .dashboard-header {
            background: #f9f9f9;
            padding: 16px;
            border-bottom: 1px solid #eee;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .user-info {
            font-size: 14px;
        }

        .user-name {
            font-weight: 600;
            color: #333;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 20px;
        }

        .stat-card {
            background: white;
            border: 1px solid #eee;
            border-radius: 12px;
            padding: 16px;
            text-align: center;
        }

        .stat-value {
            font-size: 28px;
            font-weight: 700;
            color: #1e5a96;
            margin-bottom: 4px;
        }

        .stat-label {
            font-size: 12px;
            color: #999;
        }

        .action-buttons {
            display: grid;
            grid-template-columns: 1fr;
            gap: 8px;
        }

        .action-btn {
            background: white;
            border: 1px solid #ddd;
            padding: 16px;
            border-radius: 8px;
            text-align: left;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 15px;
            font-weight: 500;
        }

        .action-btn:active {
            background: #f5f5f5;
            transform: scale(0.98);
        }

        .action-btn-icon {
            margin-right: 8px;
        }

        .completion-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 24px;
            text-align: center;
        }

        .completion-icon {
            font-size: 64px;
            margin-bottom: 16px;
            animation: bounce 0.6s ease-in-out;
        }

        @keyframes bounce {
            0% { transform: scale(0.5); opacity: 0; }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); opacity: 1; }
        }

        .completion-title {
            font-size: 24px;
            font-weight: 700;
            color: #333;
            margin-bottom: 8px;
        }

        .completion-message {
            font-size: 14px;
            color: #999;
            margin-bottom: 32px;
        }

        .bottom-nav {
            background: white;
            border-top: 1px solid #eee;
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0;
            padding: 8px 0;
        }

        .nav-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 12px 8px;
            cursor: pointer;
            transition: all 0.2s;
            color: #999;
            font-size: 12px;
            border: none;
            background: none;
        }

        .nav-item.active {
            color: #1e5a96;
        }

        .nav-icon {
            font-size: 20px;
            margin-bottom: 4px;
        }

        .nav-label {
            font-size: 11px;
            font-weight: 500;
        }
    </style>
</head>
<body>
    <div class="mobile-container">
        <div class="status-bar">
            <span>9:41</span>
            <div style="display: flex; gap: 4px;">
                <span>📶</span>
                <span>🔋</span>
            </div>
        </div>

        <!-- 로그인 페이지 -->
        <div id="loginPage" class="page active">
            <div class="login-container">
                <div class="logo">🏛️</div>
                <div class="app-title">메타도어</div>
                <div class="app-subtitle">유지보수 점검 시스템</div>

                <div class="login-card">
                    <div class="form-group">
                        <label class="form-label">아이디</label>
                        <input type="text" id="loginUsername" class="form-input" placeholder="아이디" value="admin">
                    </div>
                    <div class="form-group">
                        <label class="form-label">비밀번호</label>
                        <input type="password" id="loginPassword" class="form-input" placeholder="비밀번호" value="admin123">
                    </div>
                    <button class="btn btn-primary" onclick="login()">로그인</button>
                    <div class="login-help">권한자가 등록한 직원만<br>로그인할 수 있습니다.</div>
                </div>
            </div>
        </div>

        <!-- 대시보드 페이지 -->
        <div id="dashboardPage" class="page">
            <div class="header">
                <div class="header-title">대시보드</div>
                <div class="header-subtitle" id="userDisplay">admin님 환영합니다!</div>
            </div>
            <div class="page-content">
                <div class="dashboard-header">
                    <div class="user-info">
                        <div class="user-name" id="userNameDisplay">관리자</div>
                    </div>
                    <button class="nav-item" onclick="logout()" style="color: #999; padding: 0;">
                        <span style="font-size: 14px;">로그아웃</span>
                    </button>
                </div>

                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value" id="totalInspections">0</div>
                        <div class="stat-label">총 점검 횟수</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value" id="thisMonthInspections">0</div>
                        <div class="stat-label">이달 점검</div>
                    </div>
                </div>

                <div class="action-buttons">
                    <button class="action-btn" onclick="goToInspection()">
                        <span class="action-btn-icon">✏️</span>새 점검 입력
                    </button>
                    <button class="action-btn" onclick="showInspectionHistory()">
                        <span class="action-btn-icon">📋</span>점검 이력 보기
                    </button>
                </div>
            </div>
        </div>

        <!-- 점검 위치 선택 페이지 -->
        <div id="districtPage" class="page">
            <div class="header">
                <div class="header-title">점검 위치 선택</div>
                <div class="header-subtitle">2단계 / 3단계</div>
            </div>
            <div class="page-content">
                <div style="margin-bottom: 12px;">
                    <label class="form-label" style="padding: 0 16px;">구</label>
                    <div class="district-list" style="padding: 0 16px;">
                        <button class="district-btn" onclick="selectDistrict(this, '금정구')">금정구</button>
                        <button class="district-btn" onclick="selectDistrict(this, '기장군')">기장군</button>
                        <button class="district-btn" onclick="selectDistrict(this, '남구')">남구</button>
                        <button class="district-btn" onclick="selectDistrict(this, '동구')">동구</button>
                        <button class="district-btn" onclick="selectDistrict(this, '동래구')">동래구</button>
                        <button class="district-btn" onclick="selectDistrict(this, '부산진구')">부산진구</button>
                        <button class="district-btn" onclick="selectDistrict(this, '북구')">북구</button>
                        <button class="district-btn" onclick="selectDistrict(this, '사상구')">사상구</button>
                        <button class="district-btn" onclick="selectDistrict(this, '사하구')">사하구</button>
                        <button class="district-btn" onclick="selectDistrict(this, '서구')">서구</button>
                        <button class="district-btn" onclick="selectDistrict(this, '수영구')">수영구</button>
                        <button class="district-btn" onclick="selectDistrict(this, '연제구')">연제구</button>
                        <button class="district-btn" onclick="selectDistrict(this, '영도구')">영도구</button>
                        <button class="district-btn" onclick="selectDistrict(this, '중구')">중구</button>
                        <button class="district-btn" onclick="selectDistrict(this, '해운대구')">해운대구</button>
                    </div>
                    <label class="form-label" style="padding: 16px 16px 0 16px; margin-top: 12px;">선택하세요</label>
                </div>
            </div>
        </div>

        <!-- 점검 입력 페이지 -->
        <div id="inspectionPage" class="page">
            <div class="header">
                <div class="header-title">점검 입력</div>
                <div class="header-subtitle" id="districtDisplay">사상구 - 점검 입력 / 3단계</div>
            </div>
            <div class="page-content">
                <form class="inspection-form" id="inspectionForm">
                    <div class="form-section">
                        <div class="form-section-title">점검 항목</div>
                        <select class="select-input" id="inspectionType">
                            <option value="">-- 항목 선택 --</option>
                            <option value="외벽">외벽</option>
                            <option value="지붕">지붕</option>
                            <option value="창호">창호</option>
                            <option value="바닥">바닥</option>
                            <option value="내벽">내벽</option>
                            <option value="기타">기타</option>
                        </select>
                    </div>

                    <div class="form-section">
                        <div class="form-section-title">조사 내용</div>
                        <div style="font-size: 12px; color: #999; margin-bottom: 8px;">이상 발견 시 조사 내용을 기록하세요</div>
                        <textarea class="textarea-input" id="inspectionContent" placeholder="예: 페널 박인 → 조기화 완료"></textarea>
                    </div>

                    <div class="form-section">
                        <div class="form-section-title">사진</div>
                        <div class="image-upload" onclick="document.getElementById('imageInput').click()">
                            <div class="image-upload-icon">📷</div>
                            <div class="image-upload-text">사진을 추가하려면 탭하세요</div>
                        </div>
                        <input type="file" id="imageInput" accept="image/*">
                        <img id="imagePreview" class="image-preview" style="display: none;">
                    </div>

                    <div class="form-section">
                        <div class="form-section-title">점검 상태</div>
                        <select class="select-input" id="inspectionStatus">
                            <option value="정상">정상</option>
                            <option value="요주의">요주의</option>
                            <option value="이상">이상</option>
                        </select>
                    </div>

                    <div class="button-group" style="padding: 0 16px; margin-bottom: 20px;">
                        <button type="button" class="btn btn-secondary" onclick="goToDashboard()">저장</button>
                        <button type="submit" class="btn btn-primary" onclick="submitInspection(event)">완료</button>
                    </div>
                </form>
            </div>
        </div>

        <!-- 완료 페이지 -->
        <div id="completionPage" class="page">
            <div class="completion-container">
                <div class="completion-icon">✓</div>
                <div class="completion-title">점검이 완료되었습니다!</div>
                <div class="completion-message">점검 기록이 저장되었습니다.</div>
                <button class="btn btn-primary" onclick="goToDashboard()" style="width: 80%; max-width: 300px;">
                    대시보드로 돌아가기
                </button>
                <button class="btn btn-secondary" onclick="goToInspection()" style="width: 80%; max-width: 300px; margin-top: 8px;">
                    다음 점검
                </button>
            </div>
        </div>

        <!-- 하단 네비게이션 -->
        <div class="bottom-nav">
            <button class="nav-item active" onclick="goToDashboard()">
                <div class="nav-icon">🏠</div>
                <div class="nav-label">홈</div>
            </button>
            <button class="nav-item" onclick="goToInspection()">
                <div class="nav-icon">✏️</div>
                <div class="nav-label">점검</div>
            </button>
            <button class="nav-item" onclick="goToProfile()">
                <div class="nav-icon">👤</div>
                <div class="nav-label">설정</div>
            </button>
        </div>
    </div>

    <script>
        const localData = {
            currentUser: null,
            inspections: [],
            selectedDistrict: null
        };

        function showPage(pageId) {
            document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));
            document.getElementById(pageId).classList.add('active');

            document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
            if (pageId === 'dashboardPage') {
                document.querySelectorAll('.nav-item')[0].classList.add('active');
            } else if (pageId === 'inspectionPage' || pageId === 'districtPage') {
                document.querySelectorAll('.nav-item')[1].classList.add('active');
            }
        }

        function login() {
            const username = document.getElementById('loginUsername').value;
            const password = document.getElementById('loginPassword').value;

            if (username && password) {
                localData.currentUser = { username, name: '관리자' };
                document.getElementById('userDisplay').textContent = username + '님 환영합니다!';
                document.getElementById('userNameDisplay').textContent = username;
                goToDashboard();
            } else {
                alert('아이디와 비밀번호를 입력하세요.');
            }
        }

        function logout() {
            if (confirm('로그아웃 하시겠습니까?')) {
                localData.currentUser = null;
                document.getElementById('loginUsername').value = '';
                document.getElementById('loginPassword').value = '';
                showPage('loginPage');
            }
        }

        function goToDashboard() {
            if (!localData.currentUser) {
                showPage('loginPage');
            } else {
                document.getElementById('totalInspections').textContent = localData.inspections.length;
                const thisMonth = new Date().getMonth();
                const thisYear = new Date().getFullYear();
                const thisMonthCount = localData.inspections.filter(i => {
                    const d = new Date(i.date);
                    return d.getMonth() === thisMonth && d.getFullYear() === thisYear;
                }).length;
                document.getElementById('thisMonthInspections').textContent = thisMonthCount;
                showPage('dashboardPage');
            }
        }

        function goToInspection() {
            if (!localData.currentUser) {
                showPage('loginPage');
                return;
            }
            showPage('districtPage');
        }

        function selectDistrict(btn, district) {
            document.querySelectorAll('.district-btn').forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');
            localData.selectedDistrict = district;
            document.getElementById('districtDisplay').textContent = district + ' - 점검 입력 / 3단계';
            
            setTimeout(() => {
                document.getElementById('inspectionType').value = '';
                document.getElementById('inspectionContent').value = '';
                document.getElementById('inspectionStatus').value = '정상';
                document.getElementById('imagePreview').style.display = 'none';
                showPage('inspectionPage');
            }, 300);
        }

        document.getElementById('imageInput').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    const preview = document.getElementById('imagePreview');
                    preview.src = event.target.result;
                    preview.style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        });

        function submitInspection(e) {
            e.preventDefault();
            
            const inspection = {
                id: Date.now(),
                date: new Date().toISOString(),
                district: localData.selectedDistrict,
                type: document.getElementById('inspectionType').value,
                content: document.getElementById('inspectionContent').value,
                status: document.getElementById('inspectionStatus').value,
                image: document.getElementById('imagePreview').src
            };

            if (!inspection.type) {
                alert('점검 항목을 선택하세요.');
                return;
            }

            localData.inspections.push(inspection);
            showPage('completionPage');
        }

        function showInspectionHistory() {
            if (localData.inspections.length === 0) {
                alert('점검 이력이 없습니다.');
                return;
            }
            
            let history = '점검 이력\\n\\n';
            localData.inspections.forEach((i, idx) => {
                const date = new Date(i.date).toLocaleDateString('ko-KR');
                history += (idx + 1) + '. ' + i.district + ' - ' + i.type + ' (' + date + ')\\n';
            });
            alert(history);
        }

        function goToProfile() {
            alert('프로필 설정 (추후 추가 예정)');
        }
    </script>
</body>
</html>'''

@app.route('/health')
def health():
    return 'OK'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False, threaded=True)
