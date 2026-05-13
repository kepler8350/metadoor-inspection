import os, json
from flask import Flask, render_template_string

app = Flask(__name__)
app.secret_key = 'secure-key-metadoor'

ITEMS = ['패널', '보드', '전원', 'PC', '카메라', '스피커', '마이크', '입력장치', '하우징', '외관데코', '기타']
LOCATIONS = {
    '금정구': ['금정도심', '금정로데오', '부곡보건소'],
    '기장군': ['기장우체국', '기장행정센터', '정관중학교'],
    '남구': ['남구청', '용호문화센터', '남부경찰서'],
    '동구': ['동구청', '좌천로', '범일로'],
    '동래구': ['동래구청', '동래온천장', '명장역'],
    '부산진구': ['부산진구청', '서면역', '부산진도서관'],
    '북구': ['북구청', '구포시장', '만평동센터'],
    '사상구': ['사상육아센터', '꿈나래도서관', '주례도서관', '사상어린이도서관', '그리며들락날락', '부산도서관'],
    '사하구': ['사하구청', '감천문화마을', '다대포해수욕장'],
    '서구': ['서구청', '암남공원', '자갈치시장'],
    '수영구': ['수영구청', '광안리해수욕장', '수영도서관'],
    '연제구': ['연제구청', '거제로', '연제문화센터'],
    '영도구': ['영도구청', '영도대교', '동백섬'],
    '중구': ['중구청', '중앙대로', '국제시장'],
}

HTML = '''<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>메타도어점검</title><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:system-ui;display:flex;justify-content:center;align-items:center;min-height:100vh;background:#e8e8e8;padding:8px}#phone{width:375px;height:812px;background:#fff;border-radius:40px;border:12px solid #000;overflow:hidden;display:flex;flex-direction:column;box-shadow:0 20px 60px rgba(0,0,0,0.3)}.notch{background:#000;height:28px;display:flex;align-items:center;justify-content:center;color:#fff;font-size:8px}.statusbar{background:#000;height:24px;display:flex;justify-content:space-between;padding:0 12px;color:#fff;font-size:10px;align-items:center}.page{flex:1;display:none;flex-direction:column;overflow:hidden}.page.show{display:flex}.login-page{background:linear-gradient(135deg,#1e5a96,#154a7a);justify-content:center;align-items:center;padding:40px}.login-card{background:#fff;border-radius:16px;padding:32px;text-align:center;width:100%;max-width:320px}.logo{font-size:48px;margin-bottom:16px}.title{font-size:23px;font-weight:700;margin-bottom:8px;color:#222}.subtitle{font-size:11px;color:#999;margin-bottom:24px}input[type="text"],input[type="password"]{width:100%;padding:10px;margin-bottom:12px;border:1px solid #ddd;border-radius:8px;font-size:13px;font-family:inherit}button{width:100%;padding:11px;background:#1e5a96;color:#fff;border:none;border-radius:8px;font-weight:600;cursor:pointer;font-size:14px}.select-page{flex:1;display:flex;flex-direction:column}.header{background:linear-gradient(135deg,#1e5a96,#154a7a);color:#fff;padding:12px 16px;font-size:14px;font-weight:700;border-bottom:1px solid #0d3a5c}.step-info{font-size:10px;opacity:0.8;margin-top:2px}.grid-container{flex:1;display:grid;grid-template-columns:45% 55%;overflow:hidden}.left-panel{background:#f5f5f5;border-right:1px solid #ddd;overflow-y:auto;padding:10px}.right-panel{background:#fff;overflow-y:auto;padding:18px;display:flex;align-items:center;justify-content:center;text-align:center;color:#888;font-size:13px}.district-btn{width:100%;padding:10px;background:#fff;border:1px solid #ddd;border-radius:6px;margin-bottom:5px;font-size:13px;cursor:pointer;font-weight:500;transition:all 0.2s}.district-btn.active{background:#1e5a96;color:#fff;border-color:#1e5a96}.location-item{padding:10px;background:#f0f0f0;border:1px solid #ddd;border-radius:4px;margin-bottom:6px;font-size:12px;cursor:pointer;transition:all 0.2s}.location-item:hover{background:#e8e8e8}.inspection-page{padding:14px;overflow-y:auto;flex-direction:column}.inspection-header{background:linear-gradient(135deg,#1e5a96,#154a7a);color:#fff;padding:12px;border-radius:8px;margin-bottom:12px;text-align:center}.inspection-title{font-size:13px;font-weight:700;margin-bottom:2px}.inspection-form-group{background:#f9f9f9;padding:10px;border-radius:6px;margin-bottom:10px}.form-label{font-size:11px;font-weight:600;margin-bottom:6px;display:block;color:#222}select,textarea{width:100%;padding:8px;border:1px solid #ddd;border-radius:6px;font-size:12px;font-family:inherit;color:#333}textarea{min-height:50px;resize:vertical}.button-group{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:12px}.btn-secondary{background:#e0e0e0;color:#333;padding:10px;border:none;border-radius:6px;cursor:pointer;font-weight:600;font-size:13px}.btn-primary{background:#1e5a96;color:#fff;padding:10px;border:none;border-radius:6px;cursor:pointer;font-weight:600;font-size:13px}</style></head><body><div id="phone"><div class="notch">9:41</div><div class="statusbar"><span>📶</span><span>🔋</span></div><div class="page login-page show"><div class="login-card"><div class="logo">🏛️</div><div class="title">메타도어</div><div class="subtitle">유지보수 점검 시스템</div><input type="text" id="userid" value="admin" placeholder="아이디"><input type="password" id="userpwd" value="admin123" placeholder="비밀번호"><button onclick="doLogin()">로그인</button></div></div><div class="page select-page"><div class="header">검결과 위치 선택<div class="step-info">2단계 / 3단계</div></div><div class="grid-container"><div class="left-panel" id="district-list"></div><div class="right-panel" id="location-list">선택하세요</div></div></div><div class="page inspection-page"><div class="inspection-header"><div class="inspection-title" id="insp-title"></div><div class="step-info">3단계 / 3단계</div></div><div class="inspection-form-group"><label class="form-label">점검 항목</label><select id="item-select"></select></div><div class="inspection-form-group"><label class="form-label">조사 내용</label><textarea id="content-textarea" placeholder="이상 발견 시 조사 내용 기록"></textarea></div><div class="inspection-form-group"><label class="form-label">점검 상태</label><select id="status-select"><option>✓ 정상</option><option>✕ 이상</option></select></div><div class="button-group"><button class="btn-secondary" onclick="goPrev()">이전</button><button class="btn-primary" onclick="submit()">완료</button></div></div></div></div><script>
const ITEMS=''' + json.dumps(ITEMS, ensure_ascii=False) + ''';
const LOC=''' + json.dumps(LOCATIONS, ensure_ascii=False) + ''';
let pageIdx=0,selectDist='',selectLoc='';
function show(p){pageIdx=p;document.querySelectorAll('.page').forEach(x=>x.classList.remove('show'));document.querySelectorAll('.page')[p].classList.add('show')}
function doLogin(){if(document.getElementById('userid').value==='admin'&&document.getElementById('userpwd').value==='admin123'){loadDistricts();show(1)}}
function loadDistricts(){const c=document.getElementById('district-list');c.innerHTML='';Object.keys(LOC).forEach(k=>{const b=document.createElement('button');b.className='district-btn';b.textContent=k;b.onclick=()=>selectDistrict(k,b);c.appendChild(b)})}
function selectDistrict(k,b){document.querySelectorAll('.district-btn').forEach(x=>x.classList.remove('active'));b.classList.add('active');selectDist=k;const c=document.getElementById('location-list');c.innerHTML=LOC[k].map(x=>'<div class="location-item" onclick="selectLocation(\''+x.replace(/'/g,"\\'")+'\')">' +x+'</div>').join('')}
function selectLocation(x){selectLoc=x;document.getElementById('insp-title').textContent=selectDist+' - '+x;const s=document.getElementById('item-select');s.innerHTML='<option>-- 선택 --</option>';ITEMS.forEach(item=>{const opt=document.createElement('option');opt.value=item;opt.textContent=item;s.appendChild(opt)});show(2)}
function goPrev(){show(1)}
function submit(){const item=document.getElementById('item-select').value;if(!item||item==='-- 선택 --'){alert('점검 항목을 선택하세요');return}alert('점검이 완료되었습니다');show(1);loadDistricts()}
</script></body></html>'''

@app.route('/')
def index():
    return render_template_string(HTML)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=False)
