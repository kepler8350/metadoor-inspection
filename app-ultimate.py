import os, json
from flask import Flask, render_template_string, request, session, jsonify, redirect
import sqlite3
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'metadoor-2024-secret'
DB_PATH = '/tmp/metadoor.db'

# 인증 정보
ADMIN_USER = ('admin', 'admin123')
USER_USER = ('user', 'user123')

# 11개 점검 항목
ITEMS = ['패널', '보드', '전원', 'PC', '카메라', '스피커', '마이크', '입력장치', '하우징', '외관데코', '기타']

# 메타도어 설치 데이터 (구별 3개씩 = 45개, 40개 기준으로 일부만 표시)
LOCATIONS = {
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
    '중구': ['중구청', '중앙도서관', '항만공사']
}

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS field_data (
        id INTEGER PRIMARY KEY, district TEXT, location TEXT, month INTEGER, 
        action_content TEXT, created_at TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS remote_data (
        id INTEGER PRIMARY KEY, district TEXT, location TEXT, item TEXT, month INTEGER,
        status TEXT, detail TEXT, created_at TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

def login_req(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user' not in session: return redirect('/')
        return f(*args, **kwargs)
    return wrap

# ===== 사용자 앱 HTML =====
USER_HTML = '''<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>메타도어</title><style>
*{margin:0;padding:0;box-sizing:border-box}body{font-family:system-ui;background:#f5f5f5;display:flex;justify-content:center;align-items:center;min-height:100vh;padding:10px}
.phone{width:375px;height:812px;background:#fff;border-radius:40px;border:12px solid #000;box-shadow:0 20px 60px rgba(0,0,0,0.3);overflow:hidden;display:flex;flex-direction:column;position:relative}
.notch{background:#000;height:28px;display:flex;align-items:center;justify-content:center;font-size:10px;color:#fff}
.status{background:#000;height:24px;display:flex;justify-content:space-between;align-items:center;padding:0 12px;font-size:10px;color:#fff}
.screen{flex:1;display:none;flex-direction:column}
.screen.active{display:flex}
.login{background:linear-gradient(135deg,#1e5a96,#164a7a);justify-content:center;align-items:center;padding:40px}
.login .card{background:#fff;border-radius:16px;padding:32px;text-align:center;width:100%}
.logo{font-size:48px;margin-bottom:16px}
.login h2{font-size:24px;margin-bottom:8px;color:#333}
.login p{font-size:12px;color:#999;margin-bottom:24px}
.login input{width:100%;padding:10px;margin-bottom:12px;border:1px solid #ddd;border-radius:8px;font-size:13px}
.login button{width:100%;padding:11px;background:#1e5a96;color:#fff;border:none;border-radius:8px;font-weight:600;cursor:pointer}
.list{flex-direction:column;padding:0}
.header{background:linear-gradient(135deg,#1e5a96,#164a7a);color:#fff;padding:16px;font-size:18px;font-weight:700}
.content{flex:1;overflow-y:auto;padding:16px}
.district-btn{width:100%;padding:12px;margin-bottom:8px;background:#f0f0f0;border:1px solid #ddd;border-radius:8px;text-align:left;cursor:pointer;font-weight:500}
.district-btn.active{background:#1e5a96;color:#fff}
.location-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:16px}
.location-item{padding:12px;background:#f9f9f9;border:1px solid #ddd;border-radius:6px;cursor:pointer;font-size:12px;text-align:center}
.location-item:active{background:#1e5a96;color:#fff}
.form-group{background:#f9f9f9;padding:12px;border-radius:8px;margin-bottom:10px}
.form-group label{display:block;font-size:12px;font-weight:600;margin-bottom:6px;color:#333}
select,textarea{width:100%;padding:8px;border:1px solid #ddd;border-radius:6px;font-size:12px;font-family:inherit}
textarea{min-height:60px}
.btn-group{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:16px}
.btn{padding:10px;border:none;border-radius:6px;cursor:pointer;font-weight:600;font-size:13px}
.btn-primary{background:#1e5a96;color:#fff}
.btn-secondary{background:#e0e0e0;color:#333}
</style></head><body><div class="phone"><div class="notch">9:41</div><div class="status"><span>📶</span><span>🔋</span></div><div class="screen login active"><div class="card"><div class="logo">🏛️</div><h2>메타도어</h2><p>유지보수 점검 시스템</p><input type="text" id="user" value="user" placeholder="아이디"><input type="password" id="pass" value="user123" placeholder="비밀번호"><button onclick="login()">로그인</button></div></div><div class="screen list"><div class="header">구 선택</div><div class="content"><div id="districts"></div></div></div><div class="screen list"><div class="header">설치 위치 선택</div><div class="content"><div id="locations"></div></div></div><div class="screen list"><div class="header"><div id="title" style="font-size:16px;margin-bottom:4px"></div><div style="font-size:11px;opacity:0.8">점검 입력</div></div><div class="content"><div class="form-group"><label>점검 항목</label><select id="item"><option>-- 선택 --</option></select></div><div class="form-group"><label>조사 내용</label><textarea id="content" placeholder="이상 발견 시 기록"></textarea></div><div class="form-group"><label>점검 상태</label><select id="status"><option value="정상">✓ 정상</option><option value="이상">✕ 이상</option></select></div><div class="btn-group"><button class="btn btn-secondary" onclick="back()">이전</button><button class="btn btn-primary" onclick="submit()">완료</button></div></div></div></div></div><script>
const ITEMS = ''' + json.dumps(ITEMS, ensure_ascii=False) + ''';
const LOCATIONS = ''' + json.dumps(LOCATIONS, ensure_ascii=False) + ''';
let current = 0, sel_dist, sel_loc;

function show(s){document.querySelectorAll('.screen').forEach(x=>x.classList.remove('active'));document.querySelectorAll('.screen')[s].classList.add('active');current=s}
function login(){if(document.getElementById('user').value==='user'&&document.getElementById('pass').value==='user123'){fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({u:document.getElementById('user').value})}).then(()=>initDistricts());show(1)}}
function initDistricts(){const d=document.getElementById('districts');Object.keys(LOCATIONS).forEach(k=>{const b=document.createElement('button');b.className='district-btn';b.textContent=k;b.onclick=()=>selectDistrict(k,b);d.appendChild(b)})}
function selectDistrict(k,b){document.querySelectorAll('.district-btn').forEach(x=>x.classList.remove('active'));b.classList.add('active');sel_dist=k;const l=document.getElementById('locations');l.innerHTML='';LOCATIONS[k].forEach(loc=>{const div=document.createElement('div');div.className='location-item';div.textContent=loc;div.onclick=()=>selectLocation(loc);l.appendChild(div)})}
function selectLocation(loc){sel_loc=loc;document.getElementById('title').textContent=sel_dist+' - '+loc;ITEMS.forEach((item,i)=>{if(i===0){const opt=document.createElement('option');opt.value='';opt.textContent='-- 선택 --';document.getElementById('item').appendChild(opt)}const opt=document.createElement('option');opt.value=item;opt.textContent=item;document.getElementById('item').appendChild(opt)});show(3)}
function back(){show(2)}
function submit(){const item=document.getElementById('item').value;if(!item){alert('항목 선택');return}fetch('/api/submit',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({dist:sel_dist,loc:sel_loc,item:item,content:document.getElementById('content').value,status:document.getElementById('status').value})}).then(()=>{alert('완료');show(1)})}
initDistricts();
</script></body></html>'''

# ===== 관리자 HTML =====
ADMIN_HTML = '''<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>관리자</title><style>
*{margin:0;padding:0;box-sizing:border-box}body{font-family:system-ui;background:#f5f5f5}
.header{background:linear-gradient(135deg,#1e5a96,#164a7a);color:#fff;padding:16px 20px;display:flex;justify-content:space-between;align-items:center}
.header h1{font-size:24px}
.logout{background:rgba(255,255,255,0.2);color:#fff;border:1px solid rgba(255,255,255,0.3);padding:8px 16px;border-radius:6px;cursor:pointer}
.container{max-width:1200px;margin:0 auto;padding:20px}
.tabs{display:flex;gap:10px;margin-bottom:20px;border-bottom:2px solid #ddd}
.tab{padding:12px 20px;background:none;border:none;font-size:15px;font-weight:600;color:#666;cursor:pointer;border-bottom:3px solid transparent}
.tab.active{color:#1e5a96;border-bottom-color:#1e5a96}
.panel{display:none;background:#fff;padding:20px;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,0.06)}
.panel.active{display:block}
.filter{display:grid;grid-template-columns:200px 200px 200px auto;gap:12px;margin-bottom:20px}
.filter input,.filter select{padding:8px;border:1px solid #ddd;border-radius:6px;font-size:12px}
.filter button{padding:8px 16px;background:#1e5a96;color:#fff;border:none;border-radius:6px;cursor:pointer}
.table{width:100%;border-collapse:collapse}
.table th{padding:12px;text-align:left;font-weight:600;background:#f9f9f9;border-bottom:2px solid #ddd}
.table td{padding:12px;border-bottom:1px solid #eee}
.table tr:hover{background:#f9f9f9}
.normal{color:#4caf50;font-weight:600}
.error{color:#f44336;font-weight:600}
.layout{display:grid;grid-template-columns:250px 1fr;gap:20px}
.list{max-height:500px;overflow-y:auto;border:1px solid #ddd;border-radius:6px}
.list-item{padding:8px 12px;border-bottom:1px solid #eee;cursor:pointer}
.list-item.active{background:#1e5a96;color:#fff}
.grid-3{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:16px}
.btn-group{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:16px}
.btn{padding:10px;border:none;border-radius:6px;cursor:pointer;font-weight:600}
.btn-primary{background:#1e5a96;color:#fff}
.btn-secondary{background:#e0e0e0;color:#333}
textarea{width:100%;min-height:60px;padding:8px;border:1px solid #ddd;border-radius:6px}
</style></head><body><div class="header"><h1>🏛️ 메타도어 관리자</h1><button class="logout" onclick="logout()">로그아웃</button></div><div class="container"><div class="tabs"><button class="tab active" onclick="switchTab(0,this)">현장점검</button><button class="tab" onclick="switchTab(1,this)">원격점검</button><button class="tab" onclick="switchTab(2,this)">점검보고서</button><button class="tab" onclick="switchTab(3,this)">회원관리</button></div><div id="panel0" class="panel active"><h2 style="margin-bottom:16px">현장점검</h2><div class="filter"><select id="f-district" onchange="loadFieldLocations()"><option value="">-- 구 선택 --</option></select><select id="f-month"><option value="">-- 월 선택 --</option></select><button onclick="filterField()">검색</button></div><table class="table"><thead><tr><th>구</th><th>설치 위치</th><th>상태</th><th>조치 내용</th><th>작업</th></tr></thead><tbody id="f-table"></tbody></table></div><div id="panel1" class="panel"><h2 style="margin-bottom:16px">원격점검</h2><div class="layout"><div><label style="display:block;font-size:12px;font-weight:600;margin-bottom:8px">구</label><select id="r-district" onchange="loadRemoteLocations()" style="width:100%;margin-bottom:16px"><option value="">-- 선택 --</option></select><div class="list" id="r-locations"></div></div><div><label style="display:block;font-size:12px;font-weight:600;margin-bottom:8px">점검 항목</label><div class="grid-3" id="r-items"></div><label style="display:block;font-size:12px;font-weight:600;margin-bottom:8px;margin-top:16px">월별 상태</label><div class="grid-3" id="r-months"></div></div></div></div><div id="panel2" class="panel"><h2>점검보고서</h2><p style="color:#666;margin-top:16px">통계 및 보고서 기능</p></div><div id="panel3" class="panel"><h2>회원관리</h2><table class="table" style="margin-top:16px"><thead><tr><th>사용자</th><th>역할</th><th>상태</th></tr></thead><tbody><tr><td>admin</td><td>관리자</td><td><span class="normal">활성</span></td></tr><tr><td>user</td><td>점검원</td><td><span class="normal">활성</span></td></tr></tbody></table></div></div><script>
const ITEMS = ''' + json.dumps(ITEMS, ensure_ascii=False) + ''';
const LOCATIONS = ''' + json.dumps(LOCATIONS, ensure_ascii=False) + ''';

function initAdmin(){const dd=document.getElementById('f-district'),rd=document.getElementById('r-district');Object.keys(LOCATIONS).forEach(k=>{dd.innerHTML+='<option value="'+k+'">'+k+'</option>';rd.innerHTML+='<option value="'+k+'">'+k+'</option>'});for(let i=1;i<=12;i++)document.getElementById('f-month').innerHTML+='<option value="'+i+'">'+i+'월</option>';ITEMS.forEach(item=>{const b=document.createElement('button');b.className='btn btn-secondary';b.textContent=item;b.style.cursor='pointer';b.onclick=()=>{b.classList.toggle('btn-primary');b.classList.toggle('btn-secondary')};document.getElementById('r-items').appendChild(b)});for(let i=1;i<=12;i++){const b=document.createElement('button');b.className='btn btn-secondary';b.textContent=i+'월';b.style.cursor='pointer';b.onclick=()=>{b.classList.toggle('btn-primary');b.classList.toggle('btn-secondary')};document.getElementById('r-months').appendChild(b)}}
function switchTab(i,btn){document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));document.getElementById('panel'+i).classList.add('active');document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));btn.classList.add('active')}
function loadFieldLocations(){const dist=document.getElementById('f-district').value;const tb=document.getElementById('f-table');if(!dist){tb.innerHTML='<tr><td colspan="5" style="text-align:center;color:#999">구를 선택하세요</td></tr>';return}tb.innerHTML=LOCATIONS[dist].map(loc=>'<tr><td>'+dist+'</td><td>'+loc+'</td><td><span class="normal">정상</span></td><td>-</td><td><button style="padding:4px 8px;background:#1e5a96;color:#fff;border:none;border-radius:4px;cursor:pointer" onclick="viewDetail(\''+dist+'\',\''+loc+'\')">보기</button></td></tr>').join('')}
function filterField(){loadFieldLocations()}
function loadRemoteLocations(){const dist=document.getElementById('r-district').value;const list=document.getElementById('r-locations');if(!dist){list.innerHTML='';return}list.innerHTML=LOCATIONS[dist].map(loc=>'<div class="list-item" onclick="selectRemoteLoc(this,\''+loc+'\')">'+loc+'</div>').join('')}
function selectRemoteLoc(el,loc){document.querySelectorAll('#r-locations .list-item').forEach(x=>x.classList.remove('active'));el.classList.add('active')}
function viewDetail(dist,loc){alert(dist+' - '+loc+' 상세 내용')}
function logout(){window.location.href='/logout'}
initAdmin();
</script></body></html>'''

# ===== 라우트 =====
@app.route('/')
def index():
    return render_template_string(USER_HTML)

@app.route('/api/login', methods=['POST'])
def login():
    session['user'] = request.json.get('u')
    return jsonify({'ok': True})

@app.route('/api/submit', methods=['POST'])
def submit():
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO field_data (district,location,action_content) VALUES (?,?,?)',
              (data['dist'], data['loc'], data['content']))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})

@app.route('/admin')
def admin():
    return render_template_string(ADMIN_HTML)

@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    if data.get('u') == ADMIN_USER[0] and data.get('p') == ADMIN_USER[1]:
        session['admin'] = True
        return jsonify({'ok': True})
    return jsonify({'ok': False}), 401

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
