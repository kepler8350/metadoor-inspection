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

@app.route('/health')
def health():
    return 'OK'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
