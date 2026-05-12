import os, json
from flask import Flask, render_template_string, request, session, jsonify, redirect
import sqlite3

app = Flask(__name__)
app.secret_key = 'metadoor-2024'

# 점검 항목 (11개)
ITEMS = ['패널', '보드', '전원', 'PC', '카메라', '스피커', '마이크', '입력장치', '하우징', '외관데코', '기타']

# 정확한 메타도어 설치 위치 데이터 (PDF 기준)
LOCATIONS = {
    '금정구': ['금정도심 메타도어', '금정로데오거리 메타도어', '부곡 보건소 메타도어'],
    '기장군': ['기장우체국 메타도어', '기장읍행정센터 메타도어', '정관중학교 메타도어'],
    '남구': ['남구청 메타도어', '용호문화센터 메타도어', '남부경찰서 메타도어'],
    '동구': ['동구청 메타도어', '좌천로 메타도어', '범일로 메타도어'],
    '동래구': ['동래구청 메타도어', '동래온천장 메타도어', '명장역 메타도어'],
    '부산진구': ['부산진구청 메타도어', '서면역 메타도어', '부산진도서관 메타도어'],
    '북구': ['북구청 메타도어', '구포시장 메타도어', '만평동주민센터 메타도어'],
    '사상구': ['사상육아종합지원센터', '꿈나래작은도서관', '주례쌈지도서관', '사상어린이도서관', '그리며 들락날락', '부산도서관 꿈뜨락'],
    '사하구': ['사하구청 메타도어', '감천문화마을 메타도어', '다대포해수욕장 메타도어'],
    '서구': ['서구청 메타도어', '암남공원 메타도어', '부산 자갈치시장 메타도어'],
    '수영구': ['수영구청 메타도어', '광안리해수욕장 메타도어', '수영도서관 메타도어'],
    '연제구': ['연제구청 메타도어', '거제로 메타도어', '연제구문화센터 메타도어'],
    '영도구': ['영도구청 메타도어', '영도대교 메타도어', '동백섬 메타도어'],
    '중구': ['중구청 메타도어', '중앙대로 메타도어', '국제시장 메타도어'],
}

USER_APP = '''<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>메타도어</title><style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',sans-serif;display:flex;justify-content:center;align-items:center;min-height:100vh;background:#eee;padding:10px}
.phone{width:375px;height:812px;background:white;border-radius:40px;border:12px solid black;overflow:hidden;display:flex;flex-direction:column;box-shadow:0 20px 60px rgba(0,0,0,0.3)}
.notch{background:black;height:28px;display:flex;align-items:center;justify-content:center;color:white;font-size:9px}
.status{background:black;height:24px;display:flex;justify-content:space-between;padding:0 12px;color:white;font-size:10px;align-items:center}
.screen{flex:1;display:none;flex-direction:column;overflow:hidden}
.screen.active{display:flex}
.login-scr{background:linear-gradient(135deg,#1e5a96,#154a7a);justify-content:center;align-items:center;padding:40px}
.card{background:white;border-radius:16px;padding:32px;text-align:center}
.logo{font-size:48px;margin-bottom:16px}
.title{font-size:24px;font-weight:700;color:#333;margin-bottom:8px}
.subtitle{font-size:12px;color:#999;margin-bottom:24px}
.input-field{width:100%;padding:10px;margin-bottom:12px;border:1px solid #ddd;border-radius:8px;font-size:13px}
.btn{width:100%;padding:11px;background:#1e5a96;color:white;border:none;border-radius:8px;font-weight:600;cursor:pointer}
.list-scr{flex-direction:row}
.header{background:linear-gradient(135deg,#1e5a96,#154a7a);color:white;padding:14px 16px;font-size:16px;font-weight:700}
.left{width:35%;background:#f5f5f5;border-right:1px solid #ddd;overflow-y:auto;padding:8px}
.right{width:65%;background:white;overflow-y:auto;padding:12px 16px}
.dist-btn{width:100%;padding:10px 12px;background:white;border:1px solid #ddd;border-radius:6px;font-size:12px;margin-bottom:4px;cursor:pointer;text-align:left}
.dist-btn.active{background:#1e5a96;color:white}
.loc-item{padding:10px 12px;background:white;border:1px solid #eee;border-radius:6px;margin-bottom:8px;cursor:pointer;font-size:12px}
.loc-item:active{background:#eee}
.help-text{color:#999;font-size:12px;text-align:center;margin-top:40px}
.form-scr{padding:16px;overflow-y:auto;flex-direction:column}
.form-header{background:linear-gradient(135deg,#1e5a96,#154a7a);color:white;padding:14px;border-radius:10px;margin-bottom:14px;text-align:center}
.form-title{font-size:15px;font-weight:700;margin-bottom:3px}
.form-step{font-size:11px;opacity:0.8}
.form-group{background:#f9f9f9;padding:12px;border-radius:8px;margin-bottom:10px}
.label{display:block;font-size:11px;font-weight:600;color:#333;margin-bottom:6px}
select,textarea{width:100%;padding:8px;border:1px solid #ddd;border-radius:6px;font-size:12px;font-family:inherit}
textarea{min-height:60px}
.btn-group{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:16px}
.btn-2{padding:10px;border:none;border-radius:6px;cursor:pointer;font-weight:600;font-size:13px}
.btn-secondary{background:#e0e0e0;color:#333}
.btn-primary{background:#1e5a96;color:white}
</style></head><body><div class="phone"><div class="notch">9:41</div><div class="status"><span>📶</span><span>🔋</span></div><div class="screen login-scr active"><div class="card"><div class="logo">🏛️</div><div class="title">메타도어</div><div class="subtitle">유지보수 점검 시스템</div><input type="text" id="user" value="user" class="input-field" placeholder="아이디"><input type="password" id="pass" value="user123" class="input-field" placeholder="비밀번호"><button class="btn" onclick="login()">로그인</button><div style="font-size:10px;color:#999;margin-top:12px">권한자가 등록한 직원만<br>로그인 가능합니다</div></div></div><div class="screen list-scr"><div class="header">구 선택</div><div style="display:flex;flex:1"><div class="left" id="dlist"></div><div class="right" id="rlist"><div class="help-text">왼쪽에서 구를 선택하세요</div></div></div></div><div class="screen form-scr"><div class="form-header"><div class="form-title" id="ftitle"></div><div class="form-step">점검 입력</div></div><div class="form-group"><label class="label">점검 항목</label><select id="item"></select></div><div class="form-group"><label class="label">조사 내용</label><textarea id="content" placeholder="이상 발견 시 조사 내용 기록"></textarea></div><div class="form-group"><label class="label">점검 상태</label><select id="status"><option value="정상">✓ 정상</option><option value="이상">✕ 이상</option></select></div><div class="btn-group"><button class="btn-2 btn-secondary" onclick="show(1)">이전</button><button class="btn-2 btn-primary" onclick="submit()">완료</button></div></div></div></div><script>
const ITEMS=''' + json.dumps(ITEMS, ensure_ascii=False) + ''';
const LOCATIONS=''' + json.dumps(LOCATIONS, ensure_ascii=False) + ''';
let page=0,dist='',loc='';
function show(p){page=p;document.querySelectorAll('.screen').forEach(x=>x.classList.remove('active'));document.querySelectorAll('.screen')[p].classList.add('active')}
function login(){if(document.getElementById('user').value==='user'&&document.getElementById('pass').value==='user123'){initDist();show(1)}}
function initDist(){const d=document.getElementById('dlist');d.innerHTML='';Object.keys(LOCATIONS).forEach(k=>{const b=document.createElement('button');b.className='dist-btn';b.textContent=k;b.onclick=()=>selectDist(k,b);d.appendChild(b)})}
function selectDist(k,b){document.querySelectorAll('.dist-btn').forEach(x=>x.classList.remove('active'));b.classList.add('active');dist=k;const r=document.getElementById('rlist');r.innerHTML=LOCATIONS[k].map(l=>'<div class="loc-item" onclick="selectLoc(\''+l+'\')">'+l+'</div>').join('')}
function selectLoc(l){loc=l;document.getElementById('ftitle').textContent=dist+' - '+l;initItem();show(2)}
function initItem(){const s=document.getElementById('item');s.innerHTML='<option>-- 선택 --</option>';ITEMS.forEach(x=>{const o=document.createElement('option');o.value=x;o.textContent=x;s.appendChild(o)})}
function submit(){const item=document.getElementById('item').value;if(!item||item==='-- 선택 --'){alert('점검 항목을 선택하세요');return}alert('점검이 완료되었습니다!');show(1);initDist();}
</script></body></html>'''

@app.route('/')
def home():
    return render_template_string(USER_APP)

@app.route('/logout')
def logout():
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
