from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'metadoor-secret-key-2024'

# 데이터베이스 초기화
def init_db():
    conn = sqlite3.connect('metadoor.db')
    c = conn.cursor()
    
    # 사용자 테이블
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT)''')
    
    # 점검 기록 테이블
    c.execute('''CREATE TABLE IF NOT EXISTS inspections
                 (id INTEGER PRIMARY KEY, user_id INTEGER, location TEXT, items TEXT, 
                  signature TEXT, completed_at TIMESTAMP, FOREIGN KEY(user_id) REFERENCES users(id))''')
    
    # 부산 구 목록
    conn.commit()
    
    # 기본 관리자 계정 추가
    try:
        c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                 ('admin', generate_password_hash('admin123'), 'admin'))
        conn.commit()
    except:
        pass
    
    conn.close()

init_db()

# 로그인
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = sqlite3.connect('metadoor.db')
        c = conn.cursor()
        c.execute('SELECT id, username, role FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()
        
        if user:
            c = conn.cursor()
            c.execute('SELECT password FROM users WHERE username = ?', (username,))
            stored_password = c.fetchone()[0]
            conn.close()
            
            if check_password_hash(stored_password, password):
                session['user_id'] = user[0]
                session['username'] = user[1]
                session['role'] = user[2]
                return redirect(url_for('dashboard'))
        
        return render_template('login.html', error='로그인 실패')
    
    return render_template('login.html')

# 회원가입
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = sqlite3.connect('metadoor.db')
        c = conn.cursor()
        
        try:
            c.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                     (username, generate_password_hash(password), 'user'))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except:
            conn.close()
            return render_template('register.html', error='이미 존재하는 사용자명')
    
    return render_template('register.html')

# 대시보드
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('metadoor.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM inspections WHERE user_id = ?', (session['user_id'],))
    inspection_count = c.fetchone()[0]
    
    c.execute('SELECT * FROM inspections WHERE user_id = ? ORDER BY completed_at DESC LIMIT 5',
             (session['user_id'],))
    recent_inspections = c.fetchall()
    conn.close()
    
    return render_template('dashboard.html', 
                         username=session['username'],
                         inspection_count=inspection_count,
                         recent_inspections=recent_inspections)

# 점검 입력
@app.route('/inspection', methods=['GET', 'POST'])
def inspection():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        location = request.form.get('location')
        items_json = request.form.get('items_json')
        signature = request.form.get('signature')
        
        conn = sqlite3.connect('metadoor.db')
        c = conn.cursor()
        c.execute('INSERT INTO inspections (user_id, location, items, signature, completed_at) VALUES (?, ?, ?, ?, ?)',
                 (session['user_id'], location, items_json, signature, datetime.now()))
        conn.commit()
        conn.close()
        
        return redirect(url_for('inspection_complete'))
    
    busan_districts = ['강서구', '사상구', '동구', '영도구', '남구', '중구', '서구', '부산진구', 
                      '동래구', '남동구', '북구', '해운대구', '수영구', '연제구', '금정구']
    
    return render_template('inspection.html', districts=busan_districts)

# 점검 완료
@app.route('/inspection-complete')
def inspection_complete():
    return render_template('inspection_complete.html')

# 사용자 관리 (관리자용)
@app.route('/users')
def users():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('metadoor.db')
    c = conn.cursor()
    c.execute('SELECT id, username, role FROM users')
    all_users = c.fetchall()
    conn.close()
    
    return render_template('users.html', users=all_users)

# 점검 통계
@app.route('/statistics')
def statistics():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('metadoor.db')
    c = conn.cursor()
    
    # 지역별 점검 현황
    c.execute('SELECT location, COUNT(*) FROM inspections WHERE user_id = ? GROUP BY location',
             (session['user_id'],))
    location_stats = c.fetchall()
    
    # 월별 점검 현황
    c.execute('''SELECT strftime('%Y-%m', completed_at) as month, COUNT(*) 
                 FROM inspections WHERE user_id = ? GROUP BY month ORDER BY month DESC''',
             (session['user_id'],))
    monthly_stats = c.fetchall()
    
    conn.close()
    
    return render_template('statistics.html', 
                         location_stats=location_stats,
                         monthly_stats=monthly_stats)

# 로그아웃
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# 메인 페이지
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/health')
def health():
    return 'OK'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
