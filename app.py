import os,json,sqlite3,hashlib
from flask import Flask,Response,request,session,redirect,jsonify
from functools import wraps
from datetime import datetime

app=Flask(__name__)
app.secret_key='metadoor2024secret'
ITEMS=['패널','보드','전원','PC','카메라','스피커','마이크','입력장치','하우징','외관데코','기타']
REMOTE_ITEMS=['전원 켜짐','화면 정상','소프트웨어 실행','네트워크 연결','카메라 동작','마이크 동작','스피커 동작','모션캡처 동작','외관 청결','주변환경 정상']
LOCS={'금정구':['금정아이숲','금정체육공원','금정도서관'],'기장군':['기장어린이도서관','안데르센동화마을'],'남구':['대동골문화센터'],'동구':['애니랑 들락날락'],'동래구':['온빛어린이작은도서관','혁신어울림센터','부산사회복지종합센터','부산해양자연사박물관'],'부산진구':['부산진구 기적의도서관','전포어울더울작은도서관','부산진구어린이청소년도서관','꿈자람작은도서관'],'북구':['만덕종합사회복지관','시랑골아이누리 작은도서관','덕천도서관'],'사상구':['사상육아종합지원센터','꿈나래작은도서관','주례쌈지도서관','사상어린이도서관','그리며 들락날락','부산도서관 꿈뜨락'],'사하구':['을숙도문화회관','다대도서관','노을나루길작은도서관'],'서구':['천마니작은도서관','아동보호종합센터','한형석자유아동극장'],'수영구':['도모헌 숲속체험관','망미작은도서관'],'연제구':['부산시청','연제만화도서관'],'영도구':['풀잎작은도서관','부산복합혁신센터'],'중구':['근현대역사관'],'해운대구':['송정동 어린이작은도서관','영화의전당','반송종합사회복지관']}
DB='/tmp/metadoor.db'

def init_db():
    con=sqlite3.connect(DB)
    con.execute('''CREATE TABLE IF NOT EXISTS inspections(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        district TEXT,location TEXT,item TEXT,
        content TEXT,status TEXT,inspector TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    con.execute('''CREATE TABLE IF NOT EXISTS remote_inspections(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        district TEXT,location TEXT,check_item TEXT,
        status TEXT DEFAULT '정상',note TEXT,
        inspector TEXT,check_date TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    con.execute('''CREATE TABLE IF NOT EXISTS members(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,password TEXT,
        name TEXT,phone TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    con.commit();con.close()

def login_required(f):
    @wraps(f)
    def decorated(*a,**k):
        if not session.get('admin'):return redirect('/admin/login')
        return f(*a,**k)
    return decorated

@app.route('/')
def home():return Response(build_html(),mimetype='text/html')

@app.route('/admin/login',methods=['GET','POST'])
def admin_login():
    err=''
    if request.method=='POST':
        if request.form.get('u')=='admin' and request.form.get('p')=='admin123':
            session['admin']=True;return redirect('/admin')
        err='아이디 또는 비밀번호가 틀립니다'
    H=['<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>관리자 로그인</title>']
    H.append('<style>*{margin:0;padding:0;box-sizing:border-box}body{background:#1a5276;display:flex;align-items:center;justify-content:center;min-height:100vh;font-family:sans-serif}')
    H.append('.box{background:#fff;padding:40px;border-radius:12px;width:320px;box-shadow:0 8px 32px rgba(0,0,0,.3)}')
    H.append('h2{text-align:center;margin-bottom:24px;color:#1a5276;font-size:20px}')
    H.append('input{width:100%;padding:12px;margin-bottom:14px;border:1px solid #ddd;border-radius:6px;font-size:14px}')
    H.append('button{width:100%;padding:12px;background:#1a5276;color:#fff;border:none;border-radius:6px;font-size:15px;cursor:pointer;font-weight:600}')
    H.append('.err{color:red;font-size:13px;margin-bottom:12px;text-align:center}</style></head><body>')
    H.append('<div class="box"><h2>🔐 관리자 로그인</h2>')
    if err:H.append(f'<div class="err">{err}</div>')
    H.append('<form method="post"><input name="u" placeholder="아이디"><input name="p" type="password" placeholder="비밀번호"><button>로그인</button></form></div></body></html>')
    return ''.join(H)

@app.route('/admin/logout',methods=['POST'])
def admin_logout():
    session.pop('admin',None);return redirect('/admin/login')

@app.route('/admin')
@login_required
def admin_dash():
    init_db()
    menu=request.args.get('menu','maintenance')
    LOCS_J=json.dumps(LOCS,ensure_ascii=False)
    ITEMS_J=json.dumps(ITEMS,ensure_ascii=False)
    RITEMS_J=json.dumps(REMOTE_ITEMS,ensure_ascii=False)
    H=['<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>메타도어 관리자</title>']
    H.append('<style>')
    H.append('*{margin:0;padding:0;box-sizing:border-box;font-family:sans-serif}')
    H.append('body{display:flex;height:100vh;background:#f0f2f5;overflow:hidden}')
    H.append('.sidebar{width:200px;background:#1a5276;display:flex;flex-direction:column;flex-shrink:0}')
    H.append('.sb-logo{padding:20px 16px;color:#fff;font-size:15px;font-weight:700;border-bottom:1px solid rgba(255,255,255,.15)}')
    H.append('.sb-menu{flex:1;padding:12px 0}')
    H.append('.sb-item{display:block;padding:13px 20px;color:rgba(255,255,255,.8);font-size:13px;cursor:pointer;border:none;background:none;width:100%;text-align:left;transition:.2s}')
    H.append('.sb-item:hover,.sb-item.active{background:rgba(255,255,255,.15);color:#fff}')
    H.append('.sb-item.active{border-left:3px solid #5dade2}')
    H.append('.sb-footer{padding:16px}')
    H.append('.logout-btn{width:100%;padding:10px;background:#e74c3c;color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:13px}')
    H.append('.main{flex:1;display:flex;flex-direction:column;overflow:hidden}')
    H.append('.topbar{background:#fff;padding:14px 24px;border-bottom:1px solid #e0e0e0;display:flex;justify-content:space-between;align-items:center}')
    H.append('.topbar h1{font-size:16px;color:#333;font-weight:700}')
    H.append('.period-bar{display:flex;align-items:center;gap:10px;font-size:13px}')
    H.append('.period-bar select,.period-bar input{padding:6px 10px;border:1px solid #ddd;border-radius:6px;font-size:13px}')
    H.append('.period-bar button{padding:6px 14px;background:#1a5276;color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:13px}')
    H.append('.content{flex:1;overflow:auto;padding:16px}')
    H.append('.tbl-wrap{background:#fff;border-radius:10px;overflow:auto;box-shadow:0 2px 8px rgba(0,0,0,.08)}')
    H.append('table{border-collapse:collapse;font-size:12px;min-width:100%}')
    H.append('th{background:#1a5276;color:#fff;padding:10px 8px;text-align:center;white-space:nowrap;position:sticky;top:0;z-index:2}')
    H.append('th.loc-th{position:sticky;left:0;z-index:3;background:#1a5276;min-width:150px}')
    H.append('td{padding:8px;border-bottom:1px solid #f0f0f0;border-right:1px solid #f0f0f0;text-align:center;white-space:nowrap}')
    H.append('td.loc-td{position:sticky;left:0;background:#f8f9fa;font-weight:600;font-size:12px;text-align:left;z-index:1;border-right:2px solid #ddd}')
    H.append('td.ok{color:#27ae60;font-size:11px}')
    H.append('td.has-data{cursor:pointer;background:#fff3cd;color:#856404;font-size:11px;font-weight:600}')
    H.append('td.has-data:hover{background:#ffe082}')
    H.append('td.abnormal{cursor:pointer;background:#fadbd8;color:#c0392b;font-size:11px;font-weight:600}')
    H.append('td.no-check{color:#ccc;font-size:11px}')
    H.append('.modal{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.5);z-index:100;align-items:center;justify-content:center}')
    H.append('.modal.show{display:flex}')
    H.append('.modal-box{background:#fff;border-radius:12px;padding:28px;min-width:480px;max-width:600px;max-height:80vh;overflow-y:auto;position:relative}')
    H.append('.modal-title{font-size:16px;font-weight:700;margin-bottom:16px;color:#1a5276;border-bottom:2px solid #1a5276;padding-bottom:8px}')
    H.append('.modal-close{position:absolute;top:12px;right:16px;font-size:20px;cursor:pointer;color:#999;background:none;border:none}')
    H.append('.hist-row{padding:10px 0;border-bottom:1px solid #f0f0f0;font-size:13px}')
    H.append('.hist-row:last-child{border-bottom:none}')
    H.append('.hist-meta{color:#999;font-size:11px;margin-bottom:4px}')
    H.append('.hist-content{color:#333}')
    H.append('.form-row{margin-bottom:14px}')
    H.append('.form-row label{display:block;font-size:12px;color:#555;font-weight:600;margin-bottom:5px}')
    H.append('.form-row input,.form-row select,.form-row textarea{width:100%;padding:9px;border:1px solid #ddd;border-radius:6px;font-size:13px}')
    H.append('.form-row textarea{resize:vertical;height:80px}')
    H.append('.btn-primary{padding:10px 20px;background:#1a5276;color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:14px;font-weight:600}')
    H.append('.btn-danger{padding:7px 14px;background:#e74c3c;color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:12px}')
    H.append('.btn-sec{padding:7px 14px;background:#666;color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:12px}')
    H.append('.member-table{width:100%;border-collapse:collapse;font-size:13px}')
    H.append('.member-table th{background:#1a5276;color:#fff;padding:11px 12px;text-align:left}')
    H.append('.member-table td{padding:10px 12px;border-bottom:1px solid #f0f0f0}')
    H.append('.member-table tr:hover td{background:#f8f9fa}')
    H.append('.add-form{background:#fff;border-radius:10px;padding:20px;box-shadow:0 2px 8px rgba(0,0,0,.08);margin-bottom:16px}')
    H.append('.add-form h3{font-size:14px;font-weight:700;margin-bottom:14px;color:#1a5276}')
    H.append('.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}')
    H.append('</style>')
    H.append(f'<script>const LOCS={LOCS_J},ITEMS={ITEMS_J},REMOTE_ITEMS={RITEMS_J};let curMenu="{menu}",curYear=new Date().getFullYear(),curMonth=new Date().getMonth()+1;</script>')
    H.append('</head><body>')
    # 사이드바
    H.append('<div class="sidebar">')
    H.append('<div class="sb-logo">📊 MetaDoor 관리</div>')
    H.append('<div class="sb-menu">')
    for m,label,icon in [('maintenance','유지보수현황','🔧'),('remote','원격점검','📡'),('members','회원관리','👥')]:
        active=' active' if menu==m else ''
        H.append(f'<button class="sb-item{active}" onclick="goMenu(\'{m}\')">{icon} {label}</button>')
    H.append('</div>')
    H.append('<div class="sb-footer"><form method="post" action="/admin/logout"><button class="logout-btn">로그아웃</button></form></div>')
    H.append('</div>')
    # 메인
    H.append('<div class="main">')
    H.append('<div class="topbar">')
    H.append('<h1 id="page-title">유지보수현황</h1>')
    H.append('<div class="period-bar" id="period-bar">')
    H.append(f'<select id="sel-year" onchange="loadData()"></select>')
    H.append(f'<select id="sel-month" onchange="loadData()"></select>')
    H.append('<button onclick="loadData()">조회</button>')
    H.append('</div>')
    H.append('</div>')
    H.append('<div class="content" id="content"></div>')
    H.append('</div>')
    # 상세 이력 모달
    H.append('<div class="modal" id="hist-modal"><div class="modal-box"><button class="modal-close" onclick="closeModal(\'hist-modal\')">✕</button><div class="modal-title" id="hist-title"></div><div id="hist-body"></div></div></div>')
    # 원격점검 입력 모달
    H.append('<div class="modal" id="remote-modal"><div class="modal-box"><button class="modal-close" onclick="closeModal(\'remote-modal\')">✕</button><div class="modal-title" id="remote-modal-title">원격점검 입력</div>')
    H.append('<div id="remote-modal-body"></div></div></div>')
    H.append('<script>')
    H.append('''
function goMenu(m){
  curMenu=m;
  const titles={maintenance:"유지보수현황",remote:"원격점검",members:"회원관리"};
  document.getElementById('page-title').textContent=titles[m]||m;
  document.querySelectorAll('.sb-item').forEach(b=>b.classList.remove('active'));
  document.querySelectorAll('.sb-item').forEach(b=>{if(b.textContent.includes(titles[m]))b.classList.add('active');});
  const pb=document.getElementById('period-bar');
  pb.style.display=(m==='members')?'none':'flex';
  loadData();
  history.pushState({},'','/admin?menu='+m);
}
function initYearMonth(){
  const sy=document.getElementById('sel-year'),sm=document.getElementById('sel-month');
  const ny=new Date().getFullYear();
  sy.innerHTML='';
  for(let y=ny-2;y<=ny+1;y++){const o=document.createElement('option');o.value=y;o.textContent=y+'년';if(y===ny)o.selected=true;sy.appendChild(o);}
  sm.innerHTML='';
  const nm=new Date().getMonth()+1;
  for(let mo=1;mo<=12;mo++){const o=document.createElement('option');o.value=mo;o.textContent=mo+'월';if(mo===nm)o.selected=true;sm.appendChild(o);}
}
function loadData(){
  curYear=parseInt(document.getElementById('sel-year').value||new Date().getFullYear());
  curMonth=parseInt(document.getElementById('sel-month').value||new Date().getMonth()+1);
  if(curMenu==='maintenance')loadMaintenance();
  else if(curMenu==='remote')loadRemote();
  else loadMembers();
}
function loadMaintenance(){
  fetch(`/api/maintenance?year=${curYear}&month=${curMonth}`)
  .then(r=>r.json()).then(data=>{
    let locs=[];
    Object.entries(LOCS).forEach(([d,ls])=>ls.forEach(l=>locs.push({d,l})));
    let html='<div class="tbl-wrap"><table><thead><tr><th class="loc-th">설치위치</th>';
    ITEMS.forEach(it=>{html+=`<th>${it}</th>`;});
    html+='</tr></thead><tbody>';
    locs.forEach(({d,l})=>{
      html+=`<tr><td class="loc-td">${d}<br><span style="font-weight:400;color:#666">${l}</span></td>`;
      ITEMS.forEach(it=>{
        const key=d+'|'+l+'|'+it;
        const recs=data[key]||[];
        if(recs.length===0){html+=`<td class="ok">정상</td>`;}
        else{
          const last=recs[recs.length-1];
          html+=`<td class="${last.content?'has-data':'ok'}" onclick="showHist('${d}','${l}','${it}',${JSON.stringify(recs).replace(/</g,'&lt;')})">`;
          html+=recs.length+'건</td>';
        }
      });
      html+='</tr>';
    });
    html+='</tbody></table></div>';
    document.getElementById('content').innerHTML=html;
  });
}
function showHist(d,l,it,recs){
  document.getElementById('hist-title').textContent=d+' '+l+' - '+it;
  let html='';
  if(!recs||recs.length===0){html='<p style="color:#999;text-align:center;padding:20px">기록 없음</p>';}
  else{
    recs.slice().reverse().forEach(r=>{
      html+=`<div class="hist-row">
        <div class="hist-meta">📅 ${r.created_at} | 👤 ${r.inspector||'-'} | 상태: ${r.status||'-'}</div>
        <div class="hist-content">${r.content||'(내용 없음)'}</div>
      </div>`;
    });
  }
  document.getElementById('hist-body').innerHTML=html;
  document.getElementById('hist-modal').classList.add('show');
}
function loadRemote(){
  fetch(`/api/remote?year=${curYear}&month=${curMonth}`)
  .then(r=>r.json()).then(data=>{
    let locs=[];
    Object.entries(LOCS).forEach(([d,ls])=>ls.forEach(l=>locs.push({d,l})));
    let html='<div class="tbl-wrap"><table><thead><tr><th class="loc-th">설치위치</th>';
    REMOTE_ITEMS.forEach(it=>{html+=`<th style="max-width:80px;font-size:11px">${it}</th>`;});
    html+='</tr></thead><tbody>';
    locs.forEach(({d,l})=>{
      html+=`<tr><td class="loc-td">${d}<br><span style="font-weight:400;color:#666">${l}</span></td>`;
      REMOTE_ITEMS.forEach(it=>{
        const key=d+'|'+l+'|'+it;
        const recs=data[key]||[];
        const hasAbnormal=recs.some(r=>r.status==='이상');
        if(hasAbnormal){
          html+=`<td class="abnormal" onclick="openRemoteInput('${d}','${l}','${it}',${JSON.stringify(recs).replace(/</g,'&lt;')})">⚠️ 이상</td>`;
        }else if(recs.length>0){
          html+=`<td class="has-data" onclick="openRemoteInput('${d}','${l}','${it}',${JSON.stringify(recs).replace(/</g,'&lt;')})">확인(${recs.length})</td>`;
        }else{
          html+=`<td class="ok" onclick="openRemoteInput('${d}','${l}','${it}',[])" style="cursor:pointer">정상</td>`;
        }
      });
      html+='</tr>';
    });
    html+='</tbody></table></div>';
    document.getElementById('content').innerHTML=html;
  });
}
function openRemoteInput(d,l,it,recs){
  document.getElementById('remote-modal-title').textContent=d+' '+l+' - '+it;
  let hist='';
  if(recs&&recs.length>0){
    hist='<div style="margin-bottom:16px;background:#f8f9fa;border-radius:8px;padding:12px"><div style="font-size:12px;font-weight:700;color:#555;margin-bottom:8px">📋 점검 이력</div>';
    recs.slice().reverse().forEach(r=>{
      hist+=`<div class="hist-row"><div class="hist-meta">📅 ${r.check_date} | 👤 ${r.inspector||'-'} | 상태: <b style="color:${r.status==='이상'?'#e74c3c':'#27ae60'}">${r.status}</b></div><div class="hist-content">${r.note||'*�k�용 없음)'}</div></div>`;
    });
    hist+='</div>';
  }
  const today=new Date().toISOString().slice(0,10);
  document.getElementById('remote-modal-body').innerHTML=hist+`
    <div class="form-row"><label>점검 일자</label><input type="date" id="rc-date" value="${today}"></div>
    <div class="form-row"><label>상태</label>
      <select id="rc-status">
        <option value="정상">정상</option>
        <option value="이상">이상</option>
      </select>
    </div>
    <div class="form-row"><label>내용</label><textarea id="rc-note" placeholder="점검 내용 입력..."></textarea></div>
    <div class="form-row"><label>점검자</label><input type="text" id="rc-insp" placeholder="점검자 이름"></div>
    <button class="btn-primary" onclick="saveRemote('${d}','${l}','${it}')">저장</button>
    <button class="btn-sec" style="margin-left:8px" onclick="closeModal('remote-modal')">취소</button>
  `;
  document.getElementById('remote-modal').classList.add('show');
}
function saveRemote(d,l,it){
  const data={district:d,location:l,check_item:it,
    status:document.getElementById('rc-status').value,
    note:document.getElementById('rc-note').value,
    inspector:document.getElementById('rc-insp').value,
    check_date:document.getElementById('rc-date').value};
  fetch('/api/remote/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)})
  .then(r=>r.json()).then(()=>{closeModal('remote-modal');loadRemote();});
}
function loadMembers(){
  fetch('/api/members').then(r=>r.json()).then(members=>{
    let html=`<div class="add-form">
      <h3>➕ 회원 등록</h3>
      <div class="form-grid">
        <div class="form-row"><label>아이디</label><input type="text" id="m-id" placeholder="아이디"></div>
        <div class="form-row"><label>비밀번호</label><input type="password" id="m-pw" placeholder="비밀번호"></div>
        <div class="form-row"><label>이름</label><input type="text" id="m-name" placeholder="이름"></div>
        <div class="form-row"><label>연락처</label><input type="text" id="m-phone" placeholder="010-0000-0000"></div>
      </div>
      <button class="btn-primary" onclick="addMember()">등록</button>
    </div>`;
    html+='<div class="tbl-wrap"><table class="member-table"><thead><tr><th>#</th><th>아이디</th><th>이름</th><th>연락처</th><th>등록일</th><th>관리</th></tr></thead><tbody>';
    if(members.length===0){html+='<tr><td colspan="6" style="text-align:center;padding:30px;color:#999">등록된 회원이 없습니다</td></tr>';}
    members.forEach(m=>{
      html+=`<tr><td>${m.id}</td><td>${m.username}</td><td>${m.name}</td><td>${m.phone||'-'}</td><td>${m.created_at?.slice(0,10)||''}</td>
        <td><button class="btn-danger" onclick="delMember(${m.id},'${m.username}')">삭제</button></td></tr>`;
    });
    html+='</tbody></table></div>';
    document.getElementById('content').innerHTML=html;
  });
}
function addMember(){
  const data={username:document.getElementById('m-id').value,password:document.getElementById('m-pw').value,name:document.getElementById('m-name').value,phone:document.getElementById('m-phone').value};
  if(!data.username||!data.password||!data.name){alert('아이디, 비밀번호, 이름은 필수입니다');return;}
  fetch('/api/members/add',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)})
  .then(r=>r.json()).then(res=>{if(res.ok)loadMembers();else alert(res.error||'오류 발생');});
}
function delMember(id,uname){
  if(!confirm(uname+'를 삭제하시겠습니까?'))return;
  fetch('/api/members/'+id,{method:'DELETE'}).then(r=>r.json()).then(()=>loadMembers());
}
function closeModal(id){document.getElementById(id).classList.remove('show');}
window.onclick=e=>{if(e.target.classList.contains('modal'))e.target.classList.remove('show');};
window.onload=()=>{initYearMonth();loadData();};
''')
    H.append('</script></body></html>')
    return ''.join(H)

# API: 유지보수현황
@app.route('/api/maintenance')
@login_required
def api_maintenance():
    init_db()
    year=request.args.get('year',datetime.now().year)
    month=request.args.get('month',datetime.now().month)
    con=sqlite3.connect(DB)
    rows=con.execute(
        "SELECT district,location,item,content,status,inspector,created_at FROM inspections WHERE strftime('%Y',created_at)=? AND strftime('%m',created_at)=?",
        (str(year),str(month).zfill(2))).fetchall()
    con.close()
    data={}
    for r in rows:
        key=f"{r[0]}|{r[1]}|{r[2]}"
        if key not in data:data[key]=[]
        data[key].append({'content':r[3],'status':r[4],'inspector':r[5],'created_at':r[6]})
    return jsonify(data)

# API: 원격점검 조회
@app.route('/api/remote')
@login_required
def api_remote():
    init_db()
    year=request.args.get('year',datetime.now().year)
    month=request.args.get('month',datetime.now().month)
    con=sqlite3.connect(DB)
    rows=con.execute(
        "SELECT district,location,check_item,status,note,inspector,check_date,created_at FROM remote_inspections WHERE strftime('%Y',check_date)=? AND strftime('%m',check_date)=?",
        (str(year),str(month).zfill(2))).fetchall()
    con.close()
    data={}
    for r in rows:
        key=f"{r[0]}|{r[1]}|{r[2]}"
        if key not in data:data[key]=[]
        data[key].append({'status':r[3],'note':r[4],'inspector':r[5],'check_date':r[6],'created_at':r[7]})
    return jsonify(data)

# API: 원격점검 저장
@app.route('/api/remote/save',methods=['POST'])
@login_required
def api_remote_save():
    init_db()
    d=request.get_json(force=True)
    con=sqlite3.connect(DB)
    con.execute('INSERT INTO remote_inspections(district,location,check_item,status,note,inspector,check_date) VALUES(?,?,?,?,?,?,?)',
        (d.get('district',''),d.get('location',''),d.get('check_item',''),d.get('status','정상'),d.get('note',''),d.get('inspector',''),d.get('check_date','')))
    con.commit();con.close()
    return jsonify({'ok':True})

# API: 회원 목록
@app.route('/api/members')
@login_required
def api_members():
    init_db()
    con=sqlite3.connect(DB)
    rows=con.execute('SELECT id,username,name,phone,created_at FROM members ORDER BY id DESC').fetchall()
    con.close()
    return jsonify([{'id':r[0],"username':r[1],'name':r[2],'phone':r[3],'created_at':r[4]} for r in rows])

# API: 회원 추가
@app.route('/api/members/add',methods=['POST'])
@login_required
def api_member_add():
    init_db()
    d=request.get_json(force=True)
    pw=hashlib.sha256(d.get('password','').encode()).hexdigest()
    try:
        con=sqlite3.connect(DB)
        con.execute('INSERT INTO members(username,password,name,phone) VALUES(?,?,?,?)',
            (d.get('username',''),pw,d.get('name',''),d.get('phone','')))
        con.commit();con.close()
        return jsonify({'ok':True})
    except sqlite3.IntegrityError:
        return jsonify({'ok':False,'error':'이미 존재하는 아이디입니다'})

# API: 회원 삭제
@app.route('/api/members/<int:mid>',methods=['DELETE'])
@login_required
def api_member_del(mid):
    init_db()
    con=sqlite3.connect(DB)
    con.execute('DELETE FROM members WHERE id=?',(mid,))
    con.commit();con.close()
    return jsonify({'ok':True})

# API: 점검 저장 (모바일 앱)
@app.route('/api/inspection',methods=['POST'])
def api_save():
    init_db()
    d=request.get_json(force=True)
    con=sqlite3.connect(DB)
    con.execute('INSERT INTO inspections(district,location,item,content,status,inspector) VALUES(?,?,?,?,?,?)',
        (d.get('district',''),d.get('location',''),d.get('item',''),d.get('content',''),d.get('status','정상'),d.get('inspector','')))
    con.commit();con.close()
    return jsonify({'ok':True})

@app.route('/api/inspections')
@login_required
def api_list():
    init_db()
    con=sqlite3.connect(DB)
    rows=con.execute('SELECT * FROM inspections ORDER BY created_at DESC').fetchall()
    con.close()
    return jsonify([{'id':r[0],'district':r[1],'location':r[2],'item':r[3],'content':r[4],'status':r[5],'inspector':r[6],'created_at':r[7]} for r in rows])

def build_html():
    IT=json.dumps(ITEMS,ensure_ascii=False)
    LC=json.dumps(LOCS,ensure_ascii=False)
    H=[]
    H.append('<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>메타도어</title>')
    H.append('<style>*{margin:0;padding:0;box-sizing:border-box;font-family:sans-serif}')
    H.append('#p{width:375px;height:812px;background:#fff;border-radius:20px;overflow:hidden;position:relative;box-shadow:0 8px 32px rgba(0,0,0,.15);display:flex;flex-direction:column}')
    H.append('.n{background:#000;height:28px;display:flex;align-items:center;justify-content:space-between;padding:0 16px}')
    H.append('.s{background:#000;height:24px;display:flex;justify-content:center;align-items:center;gap:12px}')
    H.append('.pg{flex:1;display:none;flex-direction:column;overflow:hidden}')
    H.append('.lg{background:linear-gradient(135deg,#1e5a96,#154a7a);display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%}')
    H.append('.cd{background:#fff;border-radius:16px;padding:32px 24px;width:90%;box-shadow:0 4px 16px rgba(0,0,0,.2)}')
    H.append('.ico{font-size:48px;margin-bottom:8px;text-align:center}')
    H.append('.nm{font-size:18px;font-weight:700;color:#1e5a96;text-align:center;margin-bottom:24px}')
    H.append('.lbl{font-size:11px;color:#666;text-align:left;display:block;margin-bottom:4px}')
    H.append('input[type=text],input[type=password]{width:100%;padding:10px;margin-bottom:12px;border:1px solid #ddc;border-radius:8px;font-size:14px}')
    H.append('.bl{width:100%;padding:11px;background:#1e5a96;color:#fff;border:none;border-radius:8px;font-weight:600;font-size:14px;cursor:pointer}')
    H.append('.slp{flex:1;display:none;flex-direction:row;overflow:hidden}')
    H.append('.lft{width:130px;min-width:100px;background:#f5f5f5;border-right:1px solid #ddd;overflow-y:auto;padding:10px;flex-shrink:0}')
    H.append('.dbtn{width:100%;padding:10px;background:#fff;border:1px solid #ddd;border-radius:6px;margin-bottom:5px;font-size:13px;cursor:pointer}')
    H.append('.dbtn.active{background:#1e5a96;color:#fff;border-color:#1e5a96}')
    H.append('.rgt{background:#fff;overflow-y:auto;padding:8px;display:flex;flex-direction:column;flex:1;gap:4px}')
    H.append('.lbtn{width:100%;padding:10px 12px;background:#f0f0f0;border:1px solid #ddd;border-radius:6px;font-size:13px;cursor:pointer;text-align:left;box-sizing:border-box}')
    H.append('.lbtn:hover{background:#1e5a96;color:#fff}')
    H.append('.ipg{flex:1;display:none;flex-direction:column;padding:16px;overflow-y:auto;gap:12px}')
    H.append('.row{display:flex;flex-direction:column;gap:4px}')
    H.append('.row label{font-size:12px;color:#555;font-weight:600}')
    H.append('select{width:100%;padding:10px;border:1px solid #ddd;border-radius:8px;font-size:14px;background:#fff}')
    H.append('textarea{width:100%;padding:10px;border:1px solid #ddd;border-radius:8px;font-size:13px;resize:none}')
    H.append('canvas{border:1px solid #ddd;border-radius:8px;width:100%;touch-action:none}')
    H.append('.sbtn{padding:13px;background:#1e5a96;color:#fff;border:none;border-radius:10px;font-size:15px;font-weight:700;cursor:pointer;width:100%}')
    H.append('.toast{position:fixed;bottom:30px;left:50%;transform:translateX(-50%);background:rgba(0,0,0,.8);color:#fff;padding:10px 20px;border-radius:20px;font-size:13px;display:none;z-index:999}')
    H.append('body{background:#e8eef5;display:flex;align-items:center;justify-content:center;min-height:100vh}')
    H.append('</style></head><body>')
    H.append('<div id="p">')
    H.append('<div class="n"><span style="color:#fff;font-size:11px" id="cl">9:41</span><span style="color:#fff;font-size:11px">●●●</span></div>')
    H.append('<div class="pg" id="s1" style="display:flex"><div class="lg"><div class="cd">')
    H.append('<div class="ico">🚪</div><div class="nm">MetaDoor 점검</div>')
    H.append('<span class="lbl">아이디</span><input type="text" id="uid" value="admin">')
    H.append('<span class="lbl">비밀번호</span><input type="password" id="upw" value="admin123">')
    H.append('<button class="bl" onclick="fn_login()">로그인</button>')
    H.append('</div></div></div>')
    H.append('<div class="pg" id="s2"><div class="s"><span style="color:#fff;font-size:11px;font-weight:600">검결과 위치 선택</span><span style="color:#aaa;font-size:10px">2단계 / 3단계</span></div>')
    H.append('<div class="slp" id="sl" style="display:flex;flex:1"><div class="lft" id="dlist"></div><div class="rgt" id="llist"><span style="color:#ccc;font-size:13px">선택하세요</span></div></div></div>')
    H.append('<div class="pg" id="s3"><div class="s" style="justify-content:space-between;padding:0 12px"><button onclick="fn_back()" style="background:none;border:none;color:#fff;font-size:18px;cursor:pointer">←</button><span style="color:#fff;font-size:11px;font-weight:600" id="stitle">점검 입력</span><span style="font-size:10px;color:#aaa">3단계 / 3단계</span></div>')
    H.append('<div class="ipg" id="ipg" style="display:flex">')
    H.append('<div class="row"><label>점검 항목</label>')
    H.append(f'<select id="sitm"><option value="">-- 항목 선택 --</option>')
    for it in ITEMS:H.append(f'<option value="{it}">{it}</option>')
    H.append('</select></div>')
    H.append('<div class="row"><label>조치 내용</label><textarea id="scont" rows="3" placeholder="조치 내용을 입력하세요..."></textarea></div>')
    H.append('<div class="row"><label>담당자</label><input type="text" id="sinsp" placeholder="담당자 이름" style="margin-bottom:0"></div>')
    H.append('<div class="row"><label>서명</label><canvas id="sig" height="100"></canvas>')
    H.append('<button onclick="fn_clr()" style="margin-top:4px;padding:6px;background:#f5f5f5;border:1px solid #ddd;border-radius:6px;font-size:12px;cursor:pointer;width:100%">서명 지우기</button></div>')
    H.append('<button class="sbtn" onclick="fn_save()">💾 점검 저장</button></div></div>')
    H.append('<div class="toast" id="toast"></div></div>')
    H.append('<script>')
    H.append(f'const LOCS={LC},ITEMS={IT};')
    H.append('let selD="",selL="",curSt="정상";')
    H.append('const fn_login=()=>{const u=document.getElementById("uid").value,p=document.getElementById("upw").value;if(u==="admin"&&p==="admin123"){document.getElementById("s1").style.display="none";document.getElementById("s2").style.display="flex";fn_ld();}else showToast("아이디 또는 비밀번호를 확인하세요");};')
    H.append('const fn_ld=()=>{const d=document.getElementById("dlist");d.innerHTML="";Object.keys(LOCS).forEach(k=>{const b=document.createElement("button");b.className="dbtn";b.textContent=k;b.onclick=()=>fn_sel(k,b);d.appendChild(b);});};')
    H.append('const fn_sel=(d,btn)=>{selD=d;document.querySelectorAll(".dbtn").forEach(b=>b.classList.remove("active"));btn.classList.add("active");const r=document.getElementById("llist");r.innerHTML="";LOCS[d].forEach(l=>{const b=document.createElement("button");b.className="lbtn";b.textContent=l;b.onclick=()=>fn_go(l);r.appendChild(b);});};')
    H.append('const fn_go=(l)=>{selL=l;document.getElementById("stitle").textContent=selD+" / "+selL;document.getElementById("s2").style.display="none";document.getElementById("s3").style.display="flex";requestAnimationFrame(()=>requestAnimationFrame(fn_ini_canvas));};')
    H.append('const fn_back=()=>{document.getElementById("s3").style.display="none";document.getElementById("s2").style.display="flex";};')
    H.append('let drawing=false,ctx,lastX=0,lastY=0;')
    H.append('const fn_ini_canvas=()=>{const c=document.getElementById("sig");const cr=c.getBoundingClientRect();c.width=Math.round(cr.width)||300;c.height=Math.round(cr.height)||100;ctx=c.getContext("2d");ctx.strokeStyle="#000";ctx.lineWidth=2;ctx.lineCap="round";ctx.lineJoin="round";')
    H.append('c.addEventListener("mousedown",e=>{if(!ctx){const cr=c.getBoundingClientRect();c.width=Math.round(cr.width)||300;c.height=Math.round(cr.height)||100;ctx=c.getContext("2d");ctx.strokeStyle="#000";ctx.lineWidth=2;ctx.lineCap="round";ctx.lineJoin="round";}drawing=true;const r=c.getBoundingClientRect();lastX=(e.clientX-r.left)*(c.width/r.width);lastY=(e.clientY-r.top)*(c.height/r.height);});')
    H.append('c.addEventListener("mousemove",e=>{if(!drawing)return;const r=c.getBoundingClientRect();const x=(e.clientX-r.left)*(c.width/r.width);const y=(e.clientY-r.top)*(c.height/r.height);ctx.beginPath();ctx.moveTo(lastX,lastY);ctx.lineTo(x,y);ctx.stroke();[lastX,lastY]=[x,y];});')
    H.append('c.addEventListener("mouseup",()=>drawing=false);')
    H.append('c.addEventListener("touchstart",e=>{e.preventDefault();if(!ctx){const cr=c.getBoundingClientRect();c.width=Math.round(cr.width)||300;c.height=Math.round(cr.height)||100;ctx=c.getContext("2d");ctx.strokeStyle="#000";ctx.lineWidth=2;ctx.lineCap="round";ctx.lineJoin="round";}drawing=true;const t=e.touches[0],r=c.getBoundingClientRect();lastX=(t.clientX-r.left)*(c.width/r.width);lastY=(t.clientY-r.top)*(c.height/r.height);},{passive:false});')
    H.append('c.addEventListener("touchmove",e=>{e.preventDefault();const t=e.touches[0],r=c.getBoundingClientRect(),x=(t.clientX-r.left)*(c.width/r.width),y=(t.clientY-r.top)*(c.height/r.height);ctx.beginPath();ctx.moveTo(lastX,lastY);ctx.lineTo(x,y);ctx.stroke();lastX=x;lastY=y;},{passive:false});')
    H.append('c.addEventListener("touchend",()=>drawing=false);};')
    H.append('const fn_clr=()=>{if(ctx){const c=document.getElementById("sig");ctx.clearRect(0,0,c.width,c.height);}};')
    H.append('const showToast=(m)=>{const t=document.getElementById("toast");t.textContent=m;t.style.display="block";setTimeout(()=>t.style.display="none",2500);};')
    H.append('const fn_save=()=>{const itm=document.getElementById("sitm").value;if(!itm){showToast("점검 항목을 선택하세요");return;}const insp=document.getElementById("sinsp").value;if(!insp.trim()){showToast("담당자 이름을 입력하세요");return;}')
    H.append('const data={district:selD,location:selL,item:itm,content:document.getElementById("scont").value,status:"정상",inspector:insp};')
    H.append('fetch("/api/inspection",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)})')
    H.append('.then(r=>r.json()).then(()=>{showToast("✅ 저장 완료!");document.getElementById("sitm").value="";document.getElementById("scont").value="";document.getElementById("sinsp").value="";fn_clr();}).catch(()=>showToast("저장 실패. 다시 시도하세요."));};')
    H.append('window.onload=()=>{const c=document.getElementById("cl");const tick=()=>{const n=new Date();c.textContent=n.getHours()+":"+(n.getMinutes()<10?"0":"")+n.getMinutes();};tick();setInterval(tick,60000);};')
    H.append('</script></body></html>')
    return ''.join(H)

if __name__=='__main__':
    init_db()
    app.run(host='0.0.0.0',port=int(os.environ.get('PORT',5000)))
