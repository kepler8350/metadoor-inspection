import os, json
from flask import Flask, render_template_string, request, session, jsonify, redirect
import sqlite3

app = Flask(__name__)
app.secret_key = 'metadoor-2024'

# 점검 항목 (11개)
ITEMS = ['패널', '보드', '전원', 'PC', '카메라', '스피커', '마이크', '입력장치', '하우징', '외관데코', '기타']

# 과업지시서.pdf 기반 정확한 메타도어 설치 위치 데이터
LOCATIONS = {
    '금정구': [
        '금정도심 메타도어',
        '금정로데오거리 메타도어',
        '부곡 보건소 메타도어'
    ],
    '기장군': [
        '기장우체국 메타도어',
        '기장읍행정센터 메타도어',
        '정관중학교 메타도어'
    ],
    '남구': [
        '남구청 메타도어',
        '용호문화센터 메타도어',
        '남부경찰서 메타도어'
    ],
    '동구': [
        '동구청 메타도어',
        '좌천로 메타도어',
        '범일로 메타도어'
    ],
    '동래구': [
        '동래구청 메타도어',
        '동래온천장 메타도어',
        '명장역 메타도어'
    ],
    '부산진구': [
        '부산진구청 메타도어',
        '서면역 메타도어',
        '부산진도서관 메타도어'
    ],
    '북구': [
        '북구청 메타도어',
        '구포시장 메타도어',
        '만평동주민센터 메타도어'
    ],
    '사상구': [
        '사상육아종합지원센터',
        '꿈나래작은도서관',
        '주례쌈지도서관',
        '사상어린이도서관',
        '그리며 들락날락',
        '부산도서관 꿈뜨락'
    ],
    '사하구': [
        '사하구청 메타도어',
        '감천문화마을 메타도어',
        '다대포해수욕장 메타도어'
    ],
    '서구': [
        '서구청 메타도어',
        '암남공원 메타도어',
        '부산 자갈치시장 메타도어'
    ],
    '수영구': [
        '수영구청 메타도어',
        '광안리해수욕장 메타도어',
        '수영도서관 메타도어'
    ],
    '연제구': [
        '연제구청 메타도어',
        '거제로 메타도어',
        '연제구문화센터 메타도어'
    ],
    '영도구': [
        '영도구청 메타도어',
        '영도대교 메타도어',
        '동백섬 메타도어'
    ],
    '중구': [
        '중구청 메타도어',
        '중앙대로 메타도어',
        '국제시장 메타도어'
    ],
}

# 2.jpg 기반 정확한 UI 디자인
USER_APP = '''<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>메타도어</title><style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;display:flex;justify-content:center;align-items:center;min-height:100vh;background:#eee;padding:10px}
.phone{width:375px;height:812px;background:#fff;border-radius:40px;border:12px solid #000;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,0.3);display:flex;flex-direction:column}
.notch{background:#000;height:28px;display:flex;align-items:center;justify-content:center;color:#fff;font-size:9px}
.status{background:#000;height:24px;display:flex;justify-content:space-between;padding:0 12px;color:#fff;font-size:10px;align-items:center}
.screen{flex:1;display:none;flex-direction:column;overflow:hidden}
.screen.active{display:flex}
.login{background:linear-gradient(135deg,#1e5a96,#154a7a);justify-content:center;align-items:center;padding:40px}
.card{background:#fff;border-radius:16px;padding:32px;text-align:center}
.logo{font-size:48px;margin-bottom:16px}
.title{font-size:24px;font-weight:700;color:#333;margin-bottom:8px}
.subtitle{font-size:12px;color:#999;margin-bottom:24px}
input{width:100%;padding:10px;margin-bottom:12px;border:1px solid #ddd;border-radius:8px;font-size:13px}
.btn{width:100%;padding:11px;background:#1e5a96;color:#fff;border:none;border-radius:8px;font-weight:600;cursor:pointer}
.list{flex:1;display:flex;overflow:hidden}
.header{background:linear-gradient(135deg,#1e5a96,#154a7a);color:#fff;padding:14px 16px;font-size:16px;font-weight:700;border-bottom:1px solid #0d3a5c}
.left{width:40%;background:#f8f8f8;border-right:1px solid #ddd;overflow-y:auto}
.right{width:60%;background:#fff;overflow-y:auto;padding:12px 14px}
.dist-btn{width:100%;padding:11px 12px;background:#fff;border:1px solid #eee;font-size:13px;margin-bottom:6px;cursor:pointer;text-align:left;border-radius:4px}
.dist-btn.active{background:#1e5a96;color:#fff;border-color:#1e5a96;font-weight:600}
.loc-item{padding:10px 12px;background:#f0f0f0;border:1px solid #ddd;border-radius:4px;margin-bottom:8px;font-size:12px;cursor:pointer}
.loc-item:active{background:#e0e0e0}
.help{color:#999;font-size:12px;text-align:center;padding:40px 20px}
.form{padding:16px;overflow-y:auto;flex-direction:column}
.header-blue{background:linear-gradient(135deg,#1e5a96,#154a7a);color:#fff;padding:14px;border-radius:10px;margin-bottom:14px;text-align:center}
.h-title{font-size:15px;font-weight:700;margin-bottom:2px}
.h-sub{font-size:11px;opacity:0.8}
.form-group{background:#f9f9f9;padding:11px;border-radius:6px;margin-bottom:10px}
.label{font-size:11px;font-weight:600;color:#333;margin-bottom:6px;display:block}
select,textarea{width:100%;padding:8px;border:1px solid #ddd;border-radius:6px;font-size:12px;font-family:inherit}
textarea{min-height:55px}
.buttons{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:14px}
.btn2{padding:10px;border:none;border-radius:6px;cursor:pointer;font-weight:600;font-size:13px}
.btn-gray{background:#e0e0e0;color:#333}
.btn-blue{background:#1e5a96;color:#fff}
</style></head><body><div class="phone"><div class="notch">9:41</div><div class="status"><span>📶</span><span>🔋</span></div><div class="screen login active"><div class="card"><div class="logo">🏛️</div><div class="title">메타도어</div><div class="subtitle">유지보수 점검 시스템</div><input type="text" id="user" value="user" placeholder="아이디"><input type="password" id="pass" value="user123" placeholder="비밀번호"><button class="btn" onclick="login()">로그인</button><div style="font-size:10px;color:#999;margin-top:12px">권한자가 등록한<br>직원만 로그인 가능</div></div></div><div class="screen list"><div class="header">구 선택</div><div class="list"><div class="left" id="dlist"></div><div class="right" id="rlist"><div class="help">왼쪽에서 구를<br>선택하세요</div></div></div></div><div class="screen form"><div class="header-blue"><div class="h-title" id="title"></div><div class="h-sub">점검 입력</div></div><div class="form-group"><label class="label">점검 항목</label><select id="item"></select></div><div class="form-group"><label class="label">조사 내용</label><textarea id="content" placeholder="이상 발견 시 조사 내용 기록"></textarea></div><div class="form-group"><label class="label">점검 상태</label><select id="status"><option>✓ 정상</option><option>✕ 이상</option></select></div><div class="buttons"><button class="btn2 btn-gray" onclick="back()">이전</button><button class="btn2 btn-blue" onclick="submit()">완료</button></div></div></div></div><script>
const ITEMS=''' + json.dumps(ITEMS, ensure_ascii=False) + ''';
const LOC=''' + json.dumps(LOCATIONS, ensure_ascii=False) + ''';
let p=0,d='',l='';
function show(s){p=s;document.querySelectorAll('.screen').forEach(x=>x.classList.remove('active'));document.querySelectorAll('.screen')[s].classList.add('active')}
function login(){if(document.getElementById('user').value==='user'&&document.getElementById('pass').value==='user123'){init();show(1)}}
function init(){const d_list=document.getElementById('dlist');d_list.innerHTML='';Object.keys(LOC).forEach(k=>{const b=document.createElement('button');b.className='dist-btn';b.textContent=k;b.onclick=()=>pickDist(k,b);d_list.appendChild(b)})}
function pickDist(k,b){document.querySelectorAll('.dist-btn').forEach(x=>x.classList.remove('active'));b.classList.add('active');d=k;const r=document.getElementById('rlist');r.innerHTML=LOC[k].map(x=>'<div class="loc-item" onclick="pickLoc(\''+x.replace(/'/g,"\\'")+'\')">' +x+'</div>').join('')}
function pickLoc(x){l=x;document.getElementById('title').textContent=d+' - '+x;const s=document.getElementById('item');s.innerHTML='<option>-- 선택 --</option>';ITEMS.forEach(item=>{const o=document.createElement('option');o.value=item;o.textContent=item;s.appendChild(o)});show(2)}
function back(){show(1)}
function submit(){const item=document.getElementById('item').value;if(!item||item==='-- 선택 --'){alert('점검 항목을 선택하세요');return}alert('점검이 완료되었습니다!');show(1);init();}
</script></body></html>'''

@app.route('/')
def home():
    return render_template_string(USER_APP)

@app.route('/logout')
def logout():
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
