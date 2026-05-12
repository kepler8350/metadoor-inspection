import os, json
from flask import Flask, render_template_string, request, session, jsonify, redirect
import sqlite3
from functools import wraps

app = Flask(__name__)
app.secret_key = 'metadoor-2024'
DB_PATH = '/tmp/metadoor.db'

ITEMS = ['패널', '보드', '전원', 'PC', '카메라', '스피커', '마이크', '입력장치', '하우징', '외관데코', '기타']
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
    '중구': ['중구청', '중앙도서관', '항만공사'],
}

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS field (id INTEGER PRIMARY KEY, district TEXT, location TEXT, month INTEGER, action TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS remote (id INTEGER PRIMARY KEY, district TEXT, location TEXT, item TEXT, month INTEGER, status TEXT, detail TEXT)')
    conn.commit()
    conn.close()

init_db()

USER_HTML = '''<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>
*{margin:0;padding:0;box-sizing:border-box}body{font-family:system-ui;display:flex;justify-content:center;align-items:center;min-height:100vh;background:#f5f5f5;padding:10px}
.phone{width:375px;height:812px;background:white;border-radius:40px;border:12px solid black;box-shadow:0 20px 60px rgba(0,0,0,0.3);overflow:hidden;display:flex;flex-direction:column}
.notch{background:black;height:28px;display:flex;align-items:center;justify-content:center;color:white;font-size:10px}
.status{background:black;height:24px;display:flex;justify-content:space-between;padding:0 12px;color:white;font-size:10px;align-items:center}
.screen{flex:1;display:none;flex-direction:column;overflow:hidden}
.screen.active{display:flex}
.login{background:linear-gradient(135deg,#1e5a96,#164a7a);justify-content:center;align-items:center;padding:40px}
.login .card{background:white;border-radius:16px;padding:32px;text-align:center}
.logo{font-size:48px;margin-bottom:16px}
.login h2{font-size:24px;margin-bottom:8px;color:#333}
.login p{font-size:12px;color:#999;margin-bottom:24px}
.login input{width:100%;padding:10px;margin-bottom:12px;border:1px solid #ddd;border-radius:8px;font-size:13px}
.login button{width:100%;padding:11px;background:#1e5a96;color:white;border:none;border-radius:8px;font-weight:600;cursor:pointer}
.header{background:linear-gradient(135deg,#1e5a96,#164a7a);color:white;padding:16px}
.list{flex:1;overflow-y:auto;padding:16px}
.district-btn{width:100%;padding:12px;margin-bottom:8px;background:#f0f0f0;border:1px solid #ddd;border-radius:8px;cursor:pointer;font-weight:500;text-align:left}
.district-btn.active{background:#1e5a96;color:white}
.location-item{padding:12px;background:#f9f9f9;border:1px solid #ddd;border-radius:6px;margin-bottom:8px;cursor:pointer;font-size:12px}
.form-group{background:#f9f9f9;padding:12px;border-radius:8px;margin-bottom:10px}
.form-group label{display:block;font-size:12px;font-weight:600;margin-bottom:6px}
select,textarea{width:100%;padding:8px;border:1px solid #ddd;border-radius:6px;font-size:12px;font-family:inherit}
textarea{min-height:60px}
.btn-group{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:16px}
.btn{padding:10px;border:none;border-radius:6px;cursor:pointer;font-weight:600}
.btn-primary{background:#1e5a96;color:white}
.btn-secondary{background:#e0e0e0}
</style></head><body><div class="phone"><div class="notch">9:41</div><div class="status"><span>📶</span><span>🔋</span></div><div class="screen login active"><div class="card"><div class="logo">🏛️</div><h2>메타도어</h2><p>유지보수 점검 시스템</p><input type="text" id="user" value="user" placeholder="아이디"><input type="password" id="pass" value="user123"><button onclick="login()">로그인</button></div></div><div class="screen list"><div class="header">구 선택</div><div class="list" id="dlist"></div></div><div class="screen list"><div class="header">설치 위치</div><div class="list" id="llist"></div></div><div class="screen list"><div class="header"><div id="title"></div><div style="font-size:11px;opacity:0.8">점검 입력</div></div><div class="list"><div class="form-group"><label>점검 항목</label><select id="item"></select></div><div class="form-group"><label>조사 내용</label><textarea id="content"></textarea></div><div class="form-group"><label>점검 상태</label><select id="status"><option>✓ 정상</option><option>✕ 이상</option></select></div><div class="btn-group"><button class="btn btn-secondary" onclick="show(2)">이전</button><button class="btn btn-primary" onclick="submit()">완료</button></div></div></div></div></div><script>
const ITEMS=''' + json.dumps(ITEMS, ensure_ascii=False) + ''';
const LOCATIONS=''' + json.dumps(LOCATIONS, ensure_ascii=False) + ''';
let page=0,dist,loc;
function show(p){page=p;document.querySelectorAll('.screen').forEach(x=>x.classList.remove('active'));document.querySelectorAll('.screen')[p].classList.add('active')}
function login(){if(document.getElementById('user').value==='user'){initDist();show(1)}}
function initDist(){const d=document.getElementById('dlist');Object.keys(LOCATIONS).forEach(k=>{const b=document.createElement('button');b.className='district-btn';b.textContent=k;b.onclick=()=>selectDist(k,b);d.appendChild(b)})}
function selectDist(k,b){document.querySelectorAll('.district-btn').forEach(x=>x.classList.remove('active'));b.classList.add('active');dist=k;const l=document.getElementById('llist');l.innerHTML='';LOCATIONS[k].forEach(x=>{const d=document.createElement('div');d.className='location-item';d.textContent=x;d.onclick=()=>{loc=x;document.getElementById('title').textContent=k+' - '+x;initItem();show(3)};l.appendChild(d)})}
function initItem(){document.getElementById('item').innerHTML='<option>-- 선택 --</option>';ITEMS.forEach(x=>{const o=document.createElement('option');o.value=x;o.textContent=x;document.getElementById('item').appendChild(o)})}
function submit(){alert('완료');show(1)}
</script></body></html>'''

ADMIN_HTML = '''<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
*{margin:0;padding:0;box-sizing:border-box}body{font-family:system-ui;background:#f5f5f5}
.header{background:linear-gradient(135deg,#1e5a96,#164a7a);color:white;padding:16px 20px;display:flex;justify-content:space-between;align-items:center}
.header h1{font-size:24px}
.tabs{max-width:1200px;margin:0 auto;padding:20px 20px 0;display:flex;gap:10px;border-bottom:2px solid #ddd}
.tab{padding:12px 20px;background:none;border:none;font-size:15px;font-weight:600;color:#666;cursor:pointer;border-bottom:3px solid transparent}
.tab.active{color:#1e5a96;border-bottom-color:#1e5a96}
.container{max-width:1200px;margin:0 auto;padding:20px}
.panel{display:none;background:white;padding:20px;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,0.06)}
.panel.active{display:block}
.table{width:100%;border-collapse:collapse}
.table th{padding:12px;text-align:left;font-weight:600;background:#f9f9f9;border-bottom:2px solid #ddd}
.table td{padding:12px;border-bottom:1px solid #eee}
.table tr:hover{background:#f9f9f9}
.stat-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:20px;margin-bottom:20px}
.stat{background:linear-gradient(135deg,#1e5a96,#164a7a);color:white;padding:20px;border-radius:12px;text-align:center}
.stat-val{font-size:32px;font-weight:700}
.stat-lbl{font-size:12px;opacity:0.8}
</style></head><body><div class="header"><h1>🏛️ 메타도어 관리자</h1><button onclick="logout()" style="background:rgba(255,255,255,0.2);color:white;border:1px solid rgba(255,255,255,0.3);padding:8px 16px;border-radius:6px;cursor:pointer">로그아웃</button></div><div class="tabs"><button class="tab active" onclick="switchTab(0,this)">현장점검</button><button class="tab" onclick="switchTab(1,this)">원격점검</button><button class="tab" onclick="switchTab(2,this)">점검보고서</button><button class="tab" onclick="switchTab(3,this)">회원관리</button></div><div class="container"><div id="p0" class="panel active"><h2 style="margin-bottom:16px">현장점검</h2><div style="display:grid;grid-template-columns:200px 200px auto;gap:12px;margin-bottom:20px"><select id="d-dist" style="padding:8px;border:1px solid #ddd;border-radius:6px"><option>-- 구 선택 --</option></select><select id="d-month" style="padding:8px;border:1px solid #ddd;border-radius:6px"><option>-- 월 선택 --</option></select><button onclick="filterField()" style="padding:8px 16px;background:#1e5a96;color:white;border:none;border-radius:6px;cursor:pointer">검색</button></div><table class="table"><thead><tr><th>구</th><th>설치 위치</th><th>상태</th><th>조치 내용</th></tr></thead><tbody id="f-table"></tbody></table></div><div id="p1" class="panel"><h2 style="margin-bottom:16px">원격점검</h2><div style="display:grid;grid-template-columns:250px 1fr;gap:20px"><div><label style="font-size:12px;font-weight:600;display:block;margin-bottom:8px">구</label><select id="r-dist" style="width:100%;padding:8px;border:1px solid #ddd;border-radius:6px;margin-bottom:16px"><option>-- 선택 --</option></select><div id="r-locs" style="border:1px solid #ddd;border-radius:6px;overflow:hidden"></div></div><div><label style="font-size:12px;font-weight:600;display:block;margin-bottom:8px">점검 항목</label><div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:20px" id="r-items"></div><label style="font-size:12px;font-weight:600;display:block;margin-bottom:8px;margin-top:16px">월별 상태</label><div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px" id="r-months"></div></div></div></div><div id="p2" class="panel"><h2>점검보고서</h2><p style="color:#666;margin-top:16px">통계 및 보고서</p></div><div id="p3" class="panel"><h2>회원관리</h2><table class="table" style="margin-top:16px"><thead><tr><th>사용자</th><th>역할</th><th>상태</th></tr></thead><tbody><tr><td>admin</td><td>관리자</td><td style="color:#4caf50;font-weight:600">활성</td></tr><tr><td>user</td><td>점검원</td><td style="color:#4caf50;font-weight:600">활성</td></tr></tbody></table></div></div><script>
const ITEMS=''' + json.dumps(ITEMS, ensure_ascii=False) + ''';
const LOCATIONS=''' + json.dumps(LOCATIONS, ensure_ascii=False) + ''';
function initAdmin(){const dd=document.getElementById('d-dist'),rd=document.getElementById('r-dist');Object.keys(LOCATIONS).forEach(k=>{dd.innerHTML+='<option>'+k+'</option>';rd.innerHTML+='<option>'+k+'</option>'});for(let i=1;i<=12;i++)document.getElementById('d-month').innerHTML+='<option>'+i+'월</option>';ITEMS.forEach(x=>{const b=document.createElement('button');b.textContent=x;b.style.cssText='padding:8px;background:#f0f0f0;border:1px solid #ddd;border-radius:6px;cursor:pointer;font-weight:500';document.getElementById('r-items').appendChild(b)});for(let i=1;i<=12;i++){const b=document.createElement('button');b.textContent=i+'월';b.style.cssText='padding:8px;background:#f0f0f0;border:1px solid #ddd;border-radius:6px;cursor:pointer;font-weight:500';document.getElementById('r-months').appendChild(b)}}
function switchTab(i,btn){document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));document.getElementById('p'+i).classList.add('active');document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));btn.classList.add('active')}
function filterField(){const dist=document.getElementById('d-dist').value;const tb=document.getElementById('f-table');if(dist==='-- 구 선택 --'){tb.innerHTML='';return}tb.innerHTML=LOCATIONS[dist].map(loc=>'<tr><td>'+dist+'</td><td>'+loc+'</td><td style="color:#4caf50">정상</td><td>-</td></tr>').join('')}
function logout(){window.location.href='/logout'}
initAdmin();
</script></body></html>'''

@app.route('/')
def home():
    return render_template_string(USER_HTML)

@app.route('/admin')
def admin():
    return render_template_string(ADMIN_HTML)

@app.route('/logout')
def logout():
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
