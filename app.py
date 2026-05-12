from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
import os
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# 세션 설정
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# 점검 데이터 저장소 (실제로는 데이터베이스 사용)
inspection_data = {}

# 부산 구 목록
DISTRICTS = [
    '금정구', '기장군', '남구', '동구', '동래구',
    '부산진구', '북구', '사상구', '사하구', '서구',
    '수영구', '연제구', '영도구', '중구', '해운대구'
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user_id = data.get('userId')
    password = data.get('password')
    
    # 간단한 인증 (실제로는 DB에서 확인)
    if user_id and password:
        session['user_id'] = user_id
        session['logged_in'] = True
        return jsonify({'success': True, 'message': '로그인 성공'})
    
    return jsonify({'success': False, 'message': '아이디 또는 비밀번호가 올바르지 않습니다'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/districts', methods=['GET'])
def get_districts():
    return jsonify({'districts': DISTRICTS})

@app.route('/api/inspection', methods=['POST'])
def save_inspection():
    if not session.get('logged_in'):
        return jsonify({'success': False, 'message': '로그인이 필요합니다'}), 401
    
    data = request.json
    inspection_id = datetime.now().strftime('%Y%m%d%H%M%S')
    
    inspection_data[inspection_id] = {
        'user_id': session.get('user_id'),
        'district': data.get('district'),
        'inspection_item': data.get('inspectionItem'),
        'location_detail': data.get('locationDetail'),
        'action': data.get('action'),
        'signature': data.get('signature'),
        'timestamp': datetime.now().isoformat()
    }
    
    return jsonify({
        'success': True,
        'message': '점검 데이터가 저장되었습니다',
        'inspection_id': inspection_id
    })

@app.route('/api/inspections', methods=['GET'])
def get_inspections():
    if not session.get('logged_in'):
        return jsonify({'success': False, 'message': '로그인이 필요합니다'}), 401
    
    user_inspections = {
        k: v for k, v in inspection_data.items()
        if v['user_id'] == session.get('user_id')
    }
    
    return jsonify({'inspections': user_inspections})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
