import os, json
from flask import Flask, render_template_string, request, session, jsonify, redirect
import sqlite3

app = Flask(__name__)
app.secret_key = 'metadoor-2024'

ITEMS = ['패널', '보드', '전원', 'PC', '카메라', '스피커', '마이크', '입력장치', '하우징', '외관데코', '기타']

LOCATIONS = {
    '금정구': ['금정도심메타도어', '금정로데오메타도어', '부곡보건소메타도어'],
    '기장군': ['기장우체국메타도어', '기장읍행정센터메타도어', '정관중학교메타도어'],
    '남구': ['남구청메타도어', '용호문화센터메타도어', '남부경찰서메타도어'],
    '동구': ['동구청메타도어', '좌천로메타도어', '범일로메타도어'],
    '동래구': ['동래구청메타도어', '동래온천장메타도어', '명장역메타도어'],
    '부산진구': ['부산진구청메타도어', '서면역메타도어', '부산진도서관메타도어'],
    '북구': ['북구청메타도어', '구포시장메타도어', '만평동주민센터메타도어'],
    '사상구': ['사상육아종합지원센터', '꿈나래작은도서관', '주례쌈지도서관', '사상어린이도서관', '그리며들락날락', '부산도서관꿈뜨락'],
    '사하구': ['사하구청메타도어', '감천문화마을메타도어', '다대포해수욕장메타도어'],
    '서구': ['서구청메타도어', '암남공원메타도어', '부산자갈치시장메타도어'],
    '수영구': ['수영구청메타도어', '광안리해수욕장메타도어', '수영도서관메타도어'],
    '연제구': ['연제구청메타도어', '거제로메타도어', '연제구문화센터메타도어'],
    '영도구': ['영도구청메타도어', '영도대교메타도어', '동백섬메타도어'],
    '중구': ['중구청메타도어', '중앙대로메타도어', '국제시장메타도어'],
}

USER_APP = '''<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>메타도어</title><style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:system-ui;display:flex;justify-content:center;align-items:center;min-height:100vh;background:#eee;padding:10px}
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
.list{flex:1;display:flex;flex-direction:column;overflow:hidden}
.header{background:linear-gradient(135deg,#1e5a96,#154a7a);color:#fff;padding:14px 16px;font-size:15px;font-weight:700}
.sub{font-size:11px;opacity:0.8}
.content{flex:1;display:grid;grid-template-columns:45% 55%;overflow:hidden}
.left{background:#f5f5f5;border-right:1px solid #ddd;overflow-y:auto;padding:12px}
.right{background:#fff;overflow-y:auto;padding:20px;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;color:#999}
.dist-btn{width:100%;padding:10px;background:#fff;border:1px solid #ddd;border-radius:6px;margin-bottom:6px;font-size:13px;cursor:pointer;text-align:center;font-weight:500}
.dist-btn.active{background:#1e5a96;color:#fff;border-color:#1e5a96}
.loc{padding:10px;background:#f0f0f0;border:1px solid #ddd;border-radius:4px;margin-bottom:6px;font-size:12px;cursor:pointer}
.loc:active{background:#e0e0e0}
.form{padding:16px;overflow-y:auto;flex-direction:column}
.fheader{background:linear-gradient(135deg,#1e5a96,#154a7a);color:#fff;padding:14px;border-radius:10px;margin-bottom:14px;text-align:center}
.ftitle{font-size:14px;font-weight:700;margin-bottom:2px}
.fsub{font-size:11px;opacity:0.8}
.fgroup{background:#f9f9f9;padding:11px;border-radius:6px;margin-bottom:10px}
.label{font-size:11px;font-weight:600;color:#333;margin-bottom:6px;display:block}
select,textarea{width:100%;padding:8px;border:1px solid #ddd;border-radius:6px;font-size:12px;font-family:inherit}
textarea{min-height:55px}
.fbtn{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:14px}
.btn2{padding:10px;border:none;border-radius:6px;cursor:pointer;font-weight:600;font-size:13px}
.bgray{background:#e0e0e0;color:#333}
.bblue{background:#1e5a96;color:#fff}
</style></head><body><div class="phone"><div class="notch">9:41</div><div class="status"><span>📶</span><span>🔋</span></div><div class="screen login active"><div class="card"><div class="logo">🏛️</div><div class="title">메타도어</div><div class="subtitle">유지보수 점검 시스템</div><input type="text" id="uid" value="admin" placeholder="아이디"><input type="password" id="upwd" value="admin123" placeholder="비밀번호"><button class="btn" onclick="login()">로그인</button></div></div><div class="screen list"><div class="header">검결과 위치 선택<div class="sub">2단계 / 3단계</div></div><div class="content"><div class="left" id="dlist"></div><div class="right" id="rlist">선택하세요</div></div></div><div class="screen form"><div class="fheader"><div class="ftitle" id="ftit"></div><div class="fsub">3단계 / 3단계</div></div><div class="fgroup"><label class="label">점검 항목</label><select id="item"></select></div><div class="fgroup"><label class="label">조사 내용</label><textarea id="cont"></textarea></div><div class="fgroup"><label class="label">점검 상태</label><select id="stat"><option>✓ 정상</option><option>✕ 이상</option></select></div><div class="fbtn"><button class="btn2 bgray" onclick="back()">이전</button><button class="btn2 bblue" onclick="done()">완료</button></div></div></div></div><script>
const ITEMS=''' + json.dumps(ITEMS, ensure_ascii=False) + ''';
const LOC=''' + json.dumps(LOCATIONS, ensure_ascii=False) + ''';
let p=0,d='',l='';
function show(s){p=s;document.querySelectorAll('.screen').forEach(x=>x.classList.remove('active'));document.querySelectorAll('.screen')[s].classList.add('active')}
function login(){if(document.getElementById('uid').value==='admin'&&document.getElementById('upwd').value==='admin123'){init();show(1)}}
function init(){const dl=document.getElementById('dlist');dl.innerHTML='';Object.keys(LOC).forEach(k=>{const b=document.createElement('button');b.className='dist-btn';b.textContent=k;b.onclick=()=>sel(k,b);dl.appendChild(b)})}
function sel(k,b){document.querySelectorAll('.dist-btn').forEach(x=>x.classList.remove('active'));b.classList.add('active');d=k;const r=document.getElementById('rlist');r.innerHTML=LOC[k].map(x=>'<div class="loc" onclick="selLoc(\''+x.replace(/'/g,"\\'")+'\')">' +x+'</div>').join('')}
function selLoc(x){l=x;document.getElementById('ftit').textContent=d+' - '+x;const s=document.getElementById('item');s.innerHTML='<option>-- 선택 --</option>';ITEMS.forEach(i=>{const o=document.createElement('option');o.value=i;o.textContent=i;s.appendChild(o)});show(2)}
function back(){show(1)}
function done(){if(!document.getElementById('item').value||document.getElementById('item').value==='-- 선택 --'){alert('항목선택');return}alert('완료!');show(1);init();}
</script></body></html>'''

@app.route('/')
def home():
    return render_template_string(USER_APP)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
