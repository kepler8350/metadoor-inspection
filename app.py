from flask import Flask, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'metadoor-secret-key-2024')

DB_PATH = '/tmp/metadoor.db'

def init_db():
    """데이터베이스 초기화"""
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE users
                     (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT)''')
        c.execute('''CREATE TABLE inspections
                     (id INTEGER PRIMARY KEY, user_id INTEGER, location TEXT, items TEXT, 
                      completed_at TIMESTAMP, FOREIGN KEY(user_id) REFERENCES users(id))''')
        
        # 기본 관리자 계정
        c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                 ('admin', generate_password_hash('admin123'), 'admin'))
        
        conn.commit()
        conn.close()

init_db()

# 헬스체크
@app.route('/health')
def health():
    return 'OK', 200

# 메인 페이지
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# 로그인
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        error = None
        
        if not username or not password:
            error = '사용자명과 비밀번호를 입력하세요.'
        else:
            try:
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute('SELECT id, username, role, password FROM users WHERE username = ?', (username,))
                user = c.fetchone()
                conn.close()
                
                if user and check_password_hash(user[3], password):
                    session['user_id'] = user[0]
                    session['username'] = user[1]
                    session['role'] = user[2]
                    return redirect(url_for('dashboard'))
                else:
                    error = '사용자명 또는 비밀번호가 올바르지 않습니다.'
            except Exception as e:
                error = f'로그인 오류: {str(e)}'
    else:
        error = None
    
    html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>메타도어 - 로그인</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            width: 100%;
            max-width: 400px;
        }}
        h1 {{ text-align: center; color: #333; margin-bottom: 10px; font-size: 32px; }}
        .subtitle {{ text-align: center; color: #666; margin-bottom: 30px; }}
        .form-group {{ margin-bottom: 20px; }}
        label {{ display: block; margin-bottom: 5px; color: #333; font-weight: bold; }}
        input {{ width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px; font-size: 14px; }}
        input:focus {{ outline: none; border-color: #667eea; }}
        button {{ width: 100%; padding: 12px; background: #667eea; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; font-weight: bold; }}
        button:hover {{ background: #5568d3; }}
        .error {{ color: #e74c3c; margin-bottom: 20px; padding: 10px; background: #fadbd8; border-radius: 5px; text-align: center; }}
        .links {{ text-align: center; margin-top: 20px; }}
        .links a {{ color: #667eea; text-decoration: none; }}
        .links a:hover {{ text-decoration: underline; }}
        .info {{ background: #e3f2fd; border: 1px solid #90caf9; padding: 10px; border-radius: 5px; margin-top: 20px; font-size: 12px; color: #1565c0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🏛️</h1>
        <h1>메타도어</h1>
        <p class="subtitle">유지보수 점검 시스템</p>
        
        {f'<div class="error">{error}</div>' if error else ''}
        
        <form method="POST">
            <div class="form-group">
                <label>사용자명</label>
                <input type="text" name="username" required autofocus>
            </div>
            <div class="form-group">
                <label>비밀번호</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit">로그인</button>
        </form>
        
        <div class="links">
            <p><a href="/register">계정이 없으신가요? 회원가입</a></p>
        </div>
        
        <div class="info">
            <strong>테스트 계정:</strong><br>
            사용자명: admin<br>
            비밀번호: admin123
        </div>
    </div>
</body>
</html>'''
    return html

# 회원가입
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        password2 = request.form.get('password2', '').strip()
        error = None
        
        if not username or not password:
            error = '사용자명과 비밀번호를 입력하세요.'
        elif password != password2:
            error = '비밀번호가 일치하지 않습니다.'
        elif len(username) < 3:
            error = '사용자명은 최소 3자 이상이어야 합니다.'
        elif len(password) < 6:
            error = '비밀번호는 최소 6자 이상이어야 합니다.'
        else:
            try:
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                         (username, generate_password_hash(password), 'user'))
                conn.commit()
                conn.close()
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                error = '이미 존재하는 사용자명입니다.'
            except Exception as e:
                error = f'회원가입 오류: {str(e)}'
    else:
        error = None
    
    html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>메타도어 - 회원가입</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            width: 100%;
            max-width: 400px;
        }}
        h1 {{ text-align: center; color: #333; margin-bottom: 30px; }}
        .form-group {{ margin-bottom: 20px; }}
        label {{ display: block; margin-bottom: 5px; color: #333; font-weight: bold; }}
        input {{ width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px; font-size: 14px; }}
        input:focus {{ outline: none; border-color: #667eea; }}
        button {{ width: 100%; padding: 12px; background: #667eea; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; font-weight: bold; }}
        button:hover {{ background: #5568d3; }}
        .error {{ color: #e74c3c; margin-bottom: 20px; padding: 10px; background: #fadbd8; border-radius: 5px; text-align: center; }}
        .links {{ text-align: center; margin-top: 20px; }}
        .links a {{ color: #667eea; text-decoration: none; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>회원가입</h1>
        
        {f'<div class="error">{error}</div>' if error else ''}
        
        <form method="POST">
            <div class="form-group">
                <label>사용자명</label>
                <input type="text" name="username" required autofocus>
            </div>
            <div class="form-group">
                <label>비밀번호</label>
                <input type="password" name="password" required>
            </div>
            <div class="form-group">
                <label>비밀번호 확인</label>
                <input type="password" name="password2" required>
            </div>
            <button type="submit">회원가입</button>
        </form>
        
        <div class="links">
            <p><a href="/login">이미 계정이 있으신가요? 로그인</a></p>
        </div>
    </div>
</body>
</html>'''
    return html

# 대시보드
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM inspections WHERE user_id = ?', (session['user_id'],))
        inspection_count = c.fetchone()[0]
        conn.close()
    except:
        inspection_count = 0
    
    html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>메타도어 - 대시보드</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', sans-serif;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .header h1 {{ font-size: 28px; }}
        .header a {{ color: white; text-decoration: none; background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 5px; }}
        .container {{
            max-width: 1200px;
            margin: 30px auto;
            padding: 0 20px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .stat-number {{ font-size: 48px; color: #667eea; font-weight: bold; }}
        .stat-label {{ color: #666; margin-top: 10px; }}
        .actions {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }}
        .action-btn {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
            text-decoration: none;
            color: #667eea;
            font-weight: bold;
            transition: transform 0.3s;
        }}
        .action-btn:hover {{ transform: translateY(-5px); }}
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
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{inspection_count}</div>
                <div class="stat-label">총 점검 횟수</div>
            </div>
        </div>
        
        <div class="actions">
            <a href="/inspection" class="action-btn">✏️ 새 점검 입력</a>
            <a href="/statistics" class="action-btn">📊 통계 보기</a>
        </div>
    </div>
</body>
</html>'''
    return html

# 점검 입력
@app.route('/inspection', methods=['GET', 'POST'])
def inspection():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        location = request.form.get('location', '')
        
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('INSERT INTO inspections (user_id, location, items, completed_at) VALUES (?, ?, ?, ?)',
                     (session['user_id'], location, '[]', datetime.now()))
            conn.commit()
            conn.close()
            return redirect(url_for('inspection_complete'))
        except Exception as e:
            return f'오류: {str(e)}', 500
    
    busan_districts = ['강서구', '사상구', '동구', '영도구', '남구', '중구', '서구', '부산진구', 
                      '동래구', '남동구', '북구', '해운대구', '수영구', '연제구', '금정구']
    options = ''.join([f'<option value="{d}">{d}</option>' for d in busan_districts])
    
    html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>메타도어 - 점검 입력</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', sans-serif;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            display: flex;
            justify-content: space-between;
        }}
        .container {{
            max-width: 800px;
            margin: 30px auto;
            padding: 0 20px;
        }}
        .form-card {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h2 {{ margin-bottom: 30px; color: #333; }}
        .form-group {{ margin-bottom: 20px; }}
        label {{ display: block; margin-bottom: 8px; color: #333; font-weight: bold; }}
        select {{ width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 5px; font-size: 14px; }}
        select:focus {{ outline: none; border-color: #667eea; }}
        button[type="submit"] {{
            width: 100%;
            padding: 15px;
            background: #27ae60;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 20px;
        }}
        button[type="submit"]:hover {{ background: #229954; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏛️ 메타도어</h1>
        <a href="/dashboard" style="color: white; text-decoration: none;">← 대시보드</a>
    </div>
    
    <div class="container">
        <div class="form-card">
            <h2>유지보수 점검</h2>
            
            <form method="POST">
                <div class="form-group">
                    <label>점검 위치 (부산 구)</label>
                    <select name="location" required>
                        <option value="">선택하세요</option>
                        {options}
                    </select>
                </div>
                <button type="submit">점검 완료</button>
            </form>
        </div>
    </div>
</body>
</html>'''
    return html

# 점검 완료
@app.route('/inspection-complete')
def inspection_complete():
    html = '''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>메타도어 - 완료</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .container {
            background: white;
            padding: 60px 40px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            text-align: center;
            max-width: 500px;
        }
        .icon { font-size: 100px; margin-bottom: 20px; }
        h1 { color: #27ae60; font-size: 36px; margin-bottom: 20px; }
        p { color: #666; margin-bottom: 30px; font-size: 16px; }
        .button {
            display: inline-block;
            padding: 15px 30px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 10px;
            font-weight: bold;
        }
        .button:hover { background: #5568d3; }
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">✓</div>
        <h1>점검이 완료되었습니다!</h1>
        <p>점검 기록이 성공적으로 저장되었습니다.</p>
        
        <a href="/dashboard" class="button">대시보드로 돌아가기</a>
        <a href="/inspection" class="button">다음 점검</a>
    </div>
</body>
</html>'''
    return html

# 통계
@app.route('/statistics')
def statistics():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    html = '''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>메타도어 - 통계</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', sans-serif;
            background: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            display: flex;
            justify-content: space-between;
        }
        .container {
            max-width: 1200px;
            margin: 30px auto;
            padding: 0 20px;
        }
        .stat-card {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .stat-card h3 { margin-bottom: 20px; color: #333; }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        th { background: #f9f9f9; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 점검 통계</h1>
        <a href="/dashboard" style="color: white; text-decoration: none; background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 5px;">← 대시보드</a>
    </div>
    
    <div class="container">
        <div class="stat-card">
            <h3>점검 통계</h3>
            <p>통계 데이터를 조회 중입니다...</p>
        </div>
    </div>
</body>
</html>'''
    return html

# 로그아웃
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
