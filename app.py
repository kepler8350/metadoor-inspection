import os,json,sqlite3,hashlib
import os,json,sqlite3,hashlib
from flask import Flask,Response,request,session,redirect,jsonify
from functools import wraps
from datetime import datetime

app=Flask(__name__)
app.secret_key='metadoor2024secret'
ITEMS=['패널','보드','전원','PC','카메라','스피커','마이크','입력장치','하우징','외관데코','기타']
REMOTE_ITEMS=['전원 켜짐','화면 정상','소프트웨어 실행','네트워크 연결','카메라 동작','마이크 동작','스피커 동작','모션캡처 동작','외관 청결','주변환경 정상']
REMOTE_TREE={
    '디지털사이니지':{'패널':['액정','번인','터치'],'PC':['OS','CPU','MEM','파일시스템','시스템로그','악성코드'],'카메라':[],'모션캡쳐카메라':[],'스피커':[],'마이크':[]},
    '체험형콘텐츠':{'콘텐츠재생':[],'인터랙션':[],'소프트웨어':[]},
    '통신관리':{'인터넷연결':[],'네트워크':[],'원격접속':[]},
    '전원관리':{'전원공급':[],'UPS':[],'절전기능':[]},
    '안전관리':{'발열':[],'외관':[],'비상시스템':[]},
    '통합관리CMS':{'CMS서버':[],'콘텐츠동기화':[],'원격제어':[]}
}
LOCS={'금정구':['금정아이숲','금정체육공원','금정도서관'],'기장군':['기장어린이도서관','안데르센동화마을'],'남구':['대동골문화센터'],'동구':['애니랑 들락날락'],'동래구':['온빛어린이작은도서관','혁신어울림센터','부산사회복지종합센터','부산해양자연사박물관'],'부산진구':['부산진구 기적의도서관','전포어울더울작은도서관','부산진구어린이청소년도서관','꿈자람작은도서관'],'북구':['만덕종합사회복지관','시랑골아이누리 작은도서관','덕천도서관'],'사상구':['사상육아종합지원센터','꿈나래작은도서관','주례쌈지도서관','사상어린이도서관','그리며 들락날락','부산도서관 꿈뜨락'],'사하구':['을숙도문화회관','다대도서관','노을나루길작은도서관'],'서구':['천마니작은도서관','아동보호종합센터','한형석자유아동극장'],'수영구':['도모헌 숲속체험관','망미작은도서관'],'연제구':['부산시청','연제만화도서관'],'영도구':['풀잎작은도서관','부산복합혁신센터'],'중구':['근현대역사관'],'해운대구':['송정동 어린이작은도서관','영화의전당','반송종합사회복지관']}
DB=os.environ.get('DB','/data/metadoor.db')

def init_db():
    try:os.makedirs(os.path.dirname(DB),exist_ok=True)
    except:pass
    con=sqlite3.connect(DB)
    con.execute('''CREATE TABLE IF NOT EXISTS inspections(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        district TEXT,location TEXT,item TEXT,
        content TEXT,status TEXT,inspector TEXT,
        signature TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    con.execute('''CREATE TABLE IF NOT EXISTS regular_inspections(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        district TEXT,location TEXT,item TEXT,
        content TEXT,status TEXT,inspector TEXT,
        signature TEXT,manager TEXT DEFAULT '',
        images TEXT DEFAULT '',
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
        name TEXT,phone TEXT,plain_pw TEXT DEFAULT '',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    # 기존 테이블에 signature 컬럼 없으면 추가
    try:con.execute('ALTER TABLE inspections ADD COLUMN signature TEXT DEFAULT ""')
    except:pass
    try:con.execute('ALTER TABLE inspections ADD COLUMN manager TEXT DEFAULT ""')
    except:pass
    try:con.execute('ALTER TABLE inspections ADD COLUMN images TEXT DEFAULT ""')
    except:pass
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
    H.append('th{background:#1a5276;color:#fff;padding:10px 4px;text-align:center;white-space:nowrap;position:sticky;top:0;z-index:2;min-width:52px;width:52px}')
    H.append('th.loc-th{position:sticky;left:0;z-index:3;background:#1a5276;min-width:0;white-space:nowrap;max-width:90px;overflow:hidden;text-overflow:ellipsis;font-size:10px}')
    H.append('td{padding:8px 4px;border-bottom:1px solid #f0f0f0;border-right:1px solid #f0f0f0;text-align:center;white-space:nowrap;min-width:52px;width:52px}')
    H.append('td.loc-td{position:sticky;left:0;background:#f8f9fa;font-weight:600;font-size:11px;text-align:left;z-index:1;border-right:2px solid #ddd;white-space:nowrap;max-width:90px;overflow:hidden;text-overflow:ellipsis}')
    H.append('td.ok{color:#27ae60;font-size:11px}')
    H.append('td.has-data{cursor:pointer;background:#fff3cd;color:#856404;font-size:11px;font-weight:600}')
    H.append('td.has-data:hover{background:#ffe082}')
    H.append('td.abnormal{cursor:pointer;background:#fadbd8;color:#c0392b;font-size:11px;font-weight:600}')
    H.append('td.no-check{color:#ccc;font-size:11px}')
    H.append('.modal{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.5);z-index:100;align-items:center;justify-content:center}')
    H.append('.modal.show{display:flex}')
    H.append('.modal-box{background:#fff;border-radius:12px;padding:28px;min-width:480px;max-width:600px;max-height:80vh;overflow-y:auto;position:relative}')
    H.append('.modal-title{font-size:16px;font-weight:700;margin-bottom:16px;color:#1a5276;binder-bottom:2px solid #1a5276;padding-bottom:8px}')
    H.append('.modal-close{position:absolute;top:12px;right:16px;font-size:20px;cursor:pointer;color:#999;background:none;border:none}.cat-btn{padding:6px 14px;border:1.5px solid #1a5276;border-radius:20px;background:#fff;color:#1a5276;cursor:pointer;font-size:12px;font-weight:600;margin:2px;transition:all 0.15s}.cat-btn:hover,.cat-btn.active{background:#1a5276;color:#fff}')
    H.append('.hist-row{padding:10px 0;border-bottom:1px solid #f0f0f0;font-size:13px}')
    H.append('.hist-row:last-child{border-bottom:none}')
    H.append('.hist-meta{color:#999;font-size:11px;margin-bottom:4px}')
    H.append('.hist-content{color:#333}')
    H.append('.form-row{margin-bottom:14px}')
    H.append('.form-row label{display:block;font-size:12px;color:#555;font-weight:600!margin-bottom:5px}')
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
    RTREE_J=json.dumps(REMOTE_TREE,ensure_ascii=False)
    H.append(f'<script>const LOCS={LOCS_J},ITEMS={ITEMS_J},REMOTE_ITEMS={RITEMS_J};let curMenu="{menu}",curYear=new Date().getFullYear(),curMonth=new Date().getMonth()+1;</script>')
    H.append('<script>const REMOTE_TREE='+RTREE_J+';</script>')
    H.append('</head><body>')
    H.append('<div class="sidebar">')
    H.append('<div class="sb-logo">📊 MetaDoor 관리</div>')
    H.append('<div class="sb-menu">')
    for m,label,icon in [('maintenance','방문점검현황','🔧'),('remote','원격점검','📡'),('inspection','정기점검현황','📊'),('report','보고서','📋'),('members','회원관리','👥')]:
        active=' active' if menu==m else ''
        H.append(f'<button class="sb-item{active}" onclick="goMenu(\'{m}\')">{icon} {label}</button>')
    H.append('</div>')
    H.append('<div class="sb-footer"><form method="post" action="/admin/logout"><button class="logout-btn">로그아웃</button></form></div>')
    H.append('</div>')
    H.append('<div class="main">')
    H.append('<div class="topbar">')
    H.append('<h1 id="page-title">유지보수현황</h1>')
    H.append('<div class="period-bar" id="period-bar">')
    H.append(f'<select id="sel-year" onchange="loadData()"></select>')
    H.append(f'<select id="sel-month" onchange="loadData()"></select>')
    H.append('<button onclick="loadData()">조회</button>')
    H.append('<button id="btn-maint-report" onclick="printAllMaintReports()" style="background:#27ae60;color:#fff;border:none;padding:6px 16px;border-radius:4px;cursor:pointer;font-size:13px;margin-left:8px;display:none">리포트 출력</button>')
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
  const titles={maintenance:"방문점검현황",remote:"원격점검",inspection:"정기점검현황",report:"보고서",members:"회원관리"};
  document.getElementById('page-title').textContent=titles[m]||m;
  document.querySelectorAll('.sb-item').forEach(b=>b.classList.remove('active'));
  document.querySelectorAll('.sb-item').forEach(b=>{if(b.textContent.includes(titles[m]))b.classList.add('active');});
  const pb=document.getElementById('period-bar');
  pb.style.display=(m==='members'||m==='report')?'none':'flex';
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
  else if(curMenu==='inspection')loadInspection();
  else if(curMenu==='report')loadReport();
  else loadMembers();
}
function loadMaintenance(){
  window._mData={};
  fetch(`/api/maintenance?year=${curYear}&month=${curMonth}`)
  .then(r=>r.json()).then(data=>{
    let locs=[];
    window._maintData=data;
    Object.entries(LOCS).forEach(([d,ls])=>ls.forEach(l=>locs.push({d,l})));

    // 항목별 전체 건수 합계
    let itemTotals={};
    ITEMS.forEach(it=>{itemTotals[it]=0;});
    Object.entries(data).forEach(([k,recs])=>{const p=k.split('|');const it=p[2];if(it!==undefined)itemTotals[it]=(itemTotals[it]||0)+recs.length;});

    let html='<div class="tbl-wrap"><table><thead><tr><th class="loc-th">설치위치</th>';
    ITEMS.forEach(it=>{
      const cnt=itemTotals[it]||0;
      html+=`<th>${it}${cnt>0?'<br><span style="font-size:10px;font-weight:400;color:#f39c12">'+cnt+'건</span>':''}</th>`;
    });
    html+='</tr></thead><tbody>';

    locs.forEach(({d,l})=>{
      // 해당 위치 총건수
      let rowTotal=0;
      ITEMS.forEach(it=>{rowTotal+=(data[d+'|'+l+'|'+it]||[]).length;});
      const rowBadge=rowTotal>0?' <span style="font-size:10px;color:#e74c3c;font-weight:600">('+rowTotal+'건)</span>':'';

      html+=`<tr><td class="loc-td" style="cursor:pointer" onclick="showLocHist('${encodeURIComponent(d+'|'+l)}')" title="클릭: 전체 이력">${d}<br><span style="font-weight:400;color:#666">${l}${rowBadge}</span></td>`;
      ITEMS.forEach(it=>{
        const key=d+'|'+l+'|'+it;
        const recs=data[key]||[];
        window._mData[key]=recs;
        if(recs.length===0){html+=`<td class="ok">정상</td>`;}
        else{
          const last=recs[recs.length-1];
          const cls=last.content?'has-data':'ok';
          const mkey=encodeURIComponent(key);
          html+=`<td class="${cls}" onclick="showHist('${mkey}')">${recs.length}건</td>`;
        }
      });
      html+='</tr>';
    });
    html+='</tbody></table></div>';
    document.getElementById('content').innerHTML=html;
    var rb=document.getElementById('btn-maint-report');if(rb)rb.style.display='';
  });
}



function printAllMaintReports(){
  var YSIGN="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAASwAAAEsCAYAAAB5fY51AAAAKHRFWHRDcmVhdGlvbiBUaW1lAL/5IDggNiAyMDI2IDEyOjM0OjE2ICswOTAwU/RUOwAAAAd0SU1FB+oGCAMjAI0QhjMAAAAJcEhZcwAACxIAAAsSAdLdfvwAAAAEZ0FNQQAAsY8L/GEFAAAHgElEQVR42u3dbY8bJxQG0N2q//8vu0rUpI7r8fDOBc6R+iFd2Wac8OyFAebrCwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAICtPf797yh/z24AkOW4kHr21+wGAMMsX5WpsGAdz2HzXfHaZamwYD1HhtUPKiyIrzRwXl+XG3ThLH8BsLnc0LkKty36ugoL1vApcB6Fr1uOwIK4HoU/2yqkjrgwWNjVMPDIkDruImEh78Jq63mpHMddMAT3K5yuguroPnv0xUMwxw/57vgSIAbDvgS+DJjP0C+RLwXmEVSZfDkwlqFfBZufYZxtNiHPItWhv7u1VfphIltzoJ+rOSqVViGBBW3lzFGprDIJLKiXs+BTdVVBwkO53Dt+5q0qqbAgT4tlCc/zWIIrgy8L0tQElT2Cjfiy4FqLakpYNWRICH/qFTCvh/AJqwICC/qF1OPmz7ltadm2JQksTtV7qPbpjuBxQdOKL46TjJxPeh36lSxpSDku+ag+rMJiZ3fDq16d/dNQsPau4tEEFruZFVJXn5UaVo+E9zg+yI4qJ9lalHOmUtqREjypm6SP6sNHXSzbiRJSue25m0uLVCWGcuyFs7RoQZXTpkfiz6JdXwjmsFhFxJBq1bZPZ7tbaPpEYBFZ9G0tte27ewjF8ZPsrwQWkawyJOoRJDlDx2P5IoggeiWV2tZWbRZWF1RYzNZq5faIZ/yNrgCF1QuBxUytKomd5np2upbmPJeQWXqE1Xfle6V+zrt2txgGGgreUGExQ4uOOXITcO/HdR29oTmHwGKUlnNMs8OqF0F1Q2AxS4uw6t3BUzYkt7oWEggsRhl1B63XMO3qc1eoErchsFhF7vHCPQLg3WF8rd6TBO4SsoLcaqTlws1P72koOJgKi5WUHICXY8QGa0sXKggsIksNoZ4hkHsEzKx2HsGXRlSpw8Ceq+U/nZyQ+1nCqgEVFtGlDgN7hlXOz+7eW1hVEFhEUzLkGrkPUVhNJLCIJKeDR59kNwTsQGARRU4H77nKvPWSCGHVkMBittwOLqwOJrCYqaaDt9qL2GNoKag6EVhEUPN0mVTvQmW1Y26OJ7CYpSZ8atZAlbw+pd2CagCBxQwlYdVi6Ha1ELQ2bITVIAKLmUqGgq2XHLRuKx0JLFpIDZTayqo0NDycdBMCi1K5Hb92HqnFvFPLI2KYQGBRYtSEeetqSHW1OIFFqk8bhO+CIGpQqK4W48RRUqSG1ffNa1vMQXEwgcWdd3NPqWH1lfHznDZwKL+5uJIySf5pMvv1PWY91usu7PSBhaiweCcnrFLeoyYUBAq/mXTnVW7Q9Jq3+tS2VnsPheFiVFg8ax00rQKh5EEQwmpDAotfSg/Qy/lZjefJ/pxrYSOGhPxQWll9N3qf2jbnfJ7KamECix4h0zMUrg7dS6mqhNXiBNY+ciekn1+T87pH5v/vIXdOS1BtQmCtbfRTiFNeMyMcPm0RElYbMem+rohhNZOwOoDAWs/j6zo8Ujpoj7ByV44hDAnXcVVBpIZFi3PN7+aOIlU0kdpCIwJrDVfBUHrSZ49jhmcGRKS20JHAiq92orv33JNwYBiBFdtV2JRsTemxpy8C1dVBBFZMOVtfUibBW55FFfluYbT20JjAiic1bEpPUijV6knJraisDiSwYkh9mnCUs9Nnh4OwOpTAiqnkjKnenTjKvJWwOpjAmqd0ZfaMA/Ny29hLlNBkEivd52gZBDM3HY8ULTyZQIU1VuvhTKRJcOhOhTXO6nMv0dobrT0MoMIao0cl1Lu6ilS9mbviJxVWf62fzdfqPVd24jXzpcLqrXVl8H3z556fNYvqit8EVnu972ad3oGjBCkT+Mtvq0dYpa6C39HqNypoTIXVzohjXEoeNLGLE6+ZFybd2xgxCX7aUPC06yWB31p1ZuzfO+HvzFCQt/xDKCes+jh9yQYfmMOq13vR5klOvW4SCax8szrV7tWGYSC3TLrXGVVd7d55hRVJ/MNIN6JTCav9r5cKKqw0s8IKeOK32b1Rd61OrK4giwornbCCydwlfM/wDALyW/xPMzYaq64gkY7xnxnB4Q4ZZDh9SDizujHshEwnT7rPDAzDQChwaoUVaYPt7M+HZZzYWWaGlTkrqHBShSUsYHEndNoo80UCEyrt3GmiBNW7tuz8vUM3Ow4JIwXVO5HaAkvZKbCiB1XE9sBSduhAKwQV0MDKHVtQwWFW7OCCCg61UkcXVHC4FTq8oAJ+it7xrV8CfosaAIIK+J9oQWD4B1yKFAaqKuCjKKEQ6XwqIKjZ4aCqApJFOb1gZluARTgXCljGzCOCBRWQZWRoCCugyojgMAQEmhj9XEJhBQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQJJ/AOtqW3H5m/w6AAAAAElFTkSuQmCC";
  var mo=String(curMonth).padStart(2,'0'),yr=curYear;
  var pages='';
  var locs=[];
  Object.keys(LOCS).forEach(function(d){LOCS[d].forEach(function(l){locs.push({d:d,l:l});});});
  function cv(v){return (v&&v!=='정상')?v:'';}
  function signCell(name,imgSrc){
    var html='<div style="position:relative;display:inline-block;min-width:80px;min-height:44px;vertical-align:middle">';
    if(imgSrc) html+='<img src="'+imgSrc+'" style="position:absolute;top:50%;left:50%;transform:translate(-50%,-60%);height:28px;z-index:1">';
    html+='<span style="position:relative;z-index:2;font-size:9.5pt">';
    if(name) html+=name+'<br>';
    html+='(서명)</span></div>';
    return html;
  }
  locs.forEach(function(item){
    var d=item.d,l=item.l;
    var hasData=false,cm={},manager='',userSign='',inspDate='';
    ITEMS.forEach(function(it){
      var k=d+'|'+l+'|'+it;
      var arr=window._mData[k]||[];
      var last=arr.length>0?arr[arr.length-1]:null;
      cm[it]=last?cv(last.content||''):'';
      if(arr.length>0){hasData=true;
        if(!manager&&last){manager=last.manager||last.inspector||'';userSign=last.signature||'';inspDate=(last.created_at||'').slice(0,10);}}
    });
    if(!hasData)return;
    var dp=inspDate.split('-');var m2=dp[1]||mo,dy=dp[2]||'';
    var pcC=cm['보드']||'';
    var panelC=cm['패널']||'';
    var expC=cm['기타']||'';
    pages+='<div class="pg">';
    pages+='<table class="main">';
    // colgroup: 점검항목13% | 장비명1 14% | 장비명2 15% | 수량7% | 점검내용38%
    pages+='<colgroup><col style="width:13%"><col style="width:14%"><col style="width:15%"><col style="width:7%"><col style="width:38%"></colgroup>';
    // 제목
    pages+='<tr><td colspan="5" class="title">디지털 사이니지 유지관리 ( '+m2+'월 )&nbsp; 점검조치보고서</td></tr>';
    pages+='<tr><td colspan="5" class="loc">들락날락명 : '+d+' '+l+'</td></tr>';
    pages+='<tr class="hdr"><td>점검 항목</td><td colspan="2">장비명</td><td>수량</td><td>점검내용(결과)</td></tr>';
    // 디지털 사이니지
    pages+='<tr><td class="cat" rowspan="13">디지털<br>사이니지</td><td rowspan="3">86인치 패널</td><td>액정</td><td class="qty">1</td><td rowspan="3" class="cont">'+panelC+'</td></tr>';
    pages+='<tr><td>번인</td><td class="qty">1</td></tr>';
    pages+='<tr><td>터치</td><td class="qty">1</td></tr>';
    pages+='<tr><td rowspan="6">PC</td><td>OS</td><td class="qty">1</td><td rowspan="6" class="cont">'+pcC+'</td></tr>';
    pages+='<tr><td>CPU</td><td class="qty">1</td></tr>';
    pages+='<tr><td>MEM</td><td class="qty">1</td></tr>';
    pages+='<tr><td>파일시스템</td><td class="qty">1</td></tr>';
    pages+='<tr><td>시스템로그</td><td class="qty">1</td></tr>';
    pages+='<tr><td>악성코드</td><td class="qty">1</td></tr>';
    pages+='<tr><td colspan="2">카메라</td><td class="qty">1</td><td class="cont">'+cm['카메라']+'</td></tr>';
    pages+='<tr><td colspan="2">모션캐캘 카메라</td><td class="qty">1</td><td class="cont"></td></tr>';
    pages+='<tr><td colspan="2">스피커</td><td class="qty">1</td><td class="cont">'+cm['스피커']+'</td></tr>';
    pages+='<tr><td colspan="2">마이크</td><td class="qty">1</td><td class="cont">'+cm['마이크']+'</td></tr>';
    // 체험형
    pages+='<tr><td class="cat" rowspan="2">체험형콘텐츠</td><td colspan="2">교육, 영상, 게임</td><td class="qty">1</td><td rowspan="2" class="cont">'+expC+'</td></tr>';
    pages+='<tr><td colspan="2">화상통화, AI영어회화</td><td class="qty">1</td></tr>';
    // 통신/전원/안전
    pages+='<tr><td class="cat">통신관리</td><td colspan="2">연결상태</td><td class="qty">1</td><td class="cont">'+cm['하우징']+'</td></tr>';
    pages+='<tr><td class="cat">전원관리</td><td colspan="2">공급상태</td><td class="qty">1</td><td class="cont">'+cm['전원']+'</td></tr>';
    pages+='<tr><td class="cat">안전관리</td><td colspan="2">분리/탈락 등 안전상태</td><td class="qty">1</td><td class="cont">'+cm['외관데코']+'</td></tr>';
    // CMS
    pages+='<tr><td class="cat" rowspan="3">통합관리 CMS</td><td colspan="2">CMS 시스템</td><td class="qty">1</td><td rowspan="3" class="cont cms">'+''+'</td></tr>';
    pages+='<tr><td colspan="2">장비 운영현황</td><td class="qty">1</td></tr>';
    pages+='<tr><td colspan="2">콘텐츠 운영현황</td><td class="qty">1</td></tr>';
    // 점검의견
    pages+='<tr><td class="cat">점검의견</td><td colspan="4" class="opinion"></td></tr>';
    // ── 점검자/확인자: xlsx 구조 ──
    // colgroup 추가 (점검자 구역 전용 5열)
    pages+='<tr><td class="cat" rowspan="2">점검자</td><td class="sub">소속</td><td colspan="2" style="text-align:center">주식회사 프라임텍</td><td rowspan="4" class="date">점검일자<br><br>'+yr+'.&nbsp;'+m2+'.&nbsp;'+dy+'.</td></tr>';
    pages+='<tr><td class="sub">이름</td><td colspan="2" class="sign">이&nbsp;&nbsp;순&nbsp;&nbsp;규<br>'+signCell('',YSIGN)+'</td></tr>';
    pages+='<tr><td class="cat" rowspan="2">확인자</td><td class="sub">소속</td><td colspan="2" style="text-align:left;padding-left:8px">'+d+'</td></tr>';
    pages+='<tr><td class="sub">이름</td><td colspan="2" class="sign">'+signCell(manager,userSign)+'</td></tr>';
    pages+='</table></div>';
  });
  if(!pages){alert('조회된 점검 데이터가 없습니다');return;}
  var css='*{margin:0;padding:0;box-sizing:border-box}';
  css+='body{font-family:"\ub9de\uc740 \uace0\ub515","\ub098\ub214\uace0\ub515",sans-serif;font-size:9.5pt}';
  css+='.pg{width:210mm;padding:8mm 10mm;page-break-after:always}';
  css+='.main{width:100%;border-collapse:collapse}';
  css+='.main td,.main th{border:1px solid #000;vertical-align:middle;text-align:center;padding:5px 4px;word-break:keep-all;height:40px}';
  css+='.title{font-size:14pt;font-weight:bold;text-align:center;padding:16px 4px;border:none;background:#e0e0e0;height:auto}';
  css+='.loc{text-align:left;padding:5px 4px;border:none;font-size:10pt;font-weight:bold;height:auto}';
  css+='.hdr{background:#f0f0f0;font-weight:bold}';
  css+='.cat{font-weight:bold;background:#f7f7f7}';
  css+='.sub{font-weight:bold;background:#f7f7f7;width:12%}';
  css+='.qty{font-weight:bold}';
  css+='.cont{text-align:left;padding:5px 6px;vertical-align:top}';
  css+='.cms{min-height:60px}';
  css+='.opinion{min-height:80px;text-align:left;vertical-align:top;padding:5px}';
  css+='.sign{text-align:center;vertical-align:middle;padding:4px;height:60px}';
  css+='.date{text-align:center;vertical-align:middle;font-size:9.5pt;background:#f7f7f7;width:10%}';
  var html='<!DOCTYPE html><html><head><meta charset="utf-8"><style>'+css+'</style></head><body>'+pages+'</body></html>';
  var win=window.open('','_blank','width=900,height=1100');
  win.document.write(html);win.document.close();
  setTimeout(function(){win.print();},800);
}
function loadInspection(){
  window._regularData={};
  fetch(`/api/regular?year=${curYear}&month=${curMonth}`)
  .then(r=>r.json()).then(function(data){
    window._regularData=data;
    var locs=[];
    Object.keys(LOCS).forEach(function(d){LOCS[d].forEach(function(l){locs.push({d:d,l:l});});});

    // 전체 총 점검 건수
    var totalCnt=0;
    Object.keys(data).forEach(function(k){totalCnt+=(data[k]||[]).length;});
    var totalBadge=totalCnt>0?'<br><span style="font-size:10px;font-weight:400;color:#f39c12">'+totalCnt+'건</span>':'';

    var html='<div class="tbl-wrap"><table style="width:auto;min-width:320px"><thead><tr>'+
      '<th class="loc-th" style="width:220px">설치위치</th>'+
      '<th style="text-align:center;width:80px">점검'+totalBadge+'</th></tr></thead><tbody>';

    locs.forEach(function(item){
      var d=item.d,l=item.l;
      var recs=[];
      Object.keys(data).forEach(function(k){var p=k.split('|');if(p[0]===d&&p[1]===l){(data[k]||[]).forEach(function(r){recs.push(r);});}});
      var cntBadge=recs.length>0?'<br><span style="font-size:10px;color:#1a5276;font-weight:600">'+recs.length+'건</span>':'';
      html+='<tr><td class="loc-td">'+d+'<br><span style="font-weight:400;color:#666">'+l+'</span>'+cntBadge+'</td>';
      if(recs.length>0){
        var mkey=encodeURIComponent(d+'|'+l);
        html+='<td style="text-align:center"><span data-rkey="'+mkey+'" style="background:#1a5276;color:#fff;padding:3px 12px;border-radius:4px;font-size:12px;cursor:pointer" onclick="showRegularHist(this.dataset.rkey)">점검</span></td>';
      } else {
        html+='<td></td>';
      }
      html+='</tr>';
    });
    html+='</tbody></table></div>';
    document.getElementById('content').innerHTML=html;
  });
}
function showRegularHist(encodedKey){
  var key=decodeURIComponent(encodedKey);
  var parts=key.split('|');var d=parts[0],l=parts[1];
  var recs=[];
  Object.keys(window._regularData||{}).forEach(function(k2){var arr=(window._regularData||{})[k2]||[];var p=k2.split('|');if(p[0]===d&&p[1]===l)recs=recs.concat(arr);});
  if(!recs.length)return;
  var r=recs[recs.length-1];
  var imgs=[];try{imgs=JSON.parse(r.images||'[]');}catch(e){}
  var imgHtml=imgs.length?imgs.map(function(src){return '<img src="'+src+'" style="max-width:100%;max-height:120px;object-fit:contain;border-radius:6px;cursor:pointer" onclick="openPhotoPopup(this.src)">';}).join(''):'없음';
  var sigHtml=r.signature?'<img src="'+r.signature+'" style="max-width:200px;max-height:80px;border:1px solid #ddd;border-radius:4px">':'없음';
  var pop=document.getElementById('reg-hist-pop');
  if(!pop){pop=document.createElement('div');pop.id='reg-hist-pop';pop.style.cssText='position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);z-index:9999;display:flex;align-items:center;justify-content:center';document.body.appendChild(pop);}
  var html='<div style="background:#fff;border-radius:12px;padding:24px;width:380px;max-width:95vw;max-height:85vh;overflow-y:auto;box-shadow:0 8px 32px rgba(0,0,0,0.3)">';
  html+='<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">';
  html+='<h3 style="margin:0;font-size:16px;color:#1a5276">정기점검 상세</h3>';
  html+='<button id="reg-close-btn" style="background:none;border:none;font-size:20px;cursor:pointer">&times;</button></div>';
  html+='<p style="font-size:13px;color:#555;margin:6px 0"><b>설치위치:</b> '+d+' '+l+'</p>';
  html+='<p style="font-size:13px;color:#555;margin:6px 0"><b>점검일:</b> '+((r.created_at||'').slice(0,10))+'</p>';
  html+='<p style="font-size:13px;color:#555;margin:6px 0"><b>담당자:</b> '+(r.manager||r.inspector||'-')+'</p>';
  html+='<div style="margin:10px 0"><b style="font-size:13px;color:#555">서명:</b><br>'+sigHtml+'</div>';
  html+='<div style="margin:10px 0"><b style="font-size:13px;color:#555">사진:</b><div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:4px">'+imgHtml+'</div></div>';
  html+='<div style="display:flex;gap:8px;justify-content:flex-end;margin-top:16px">';
  html+='<button id="reg-del-btn" data-rid="'+r.id+'" data-rkey="'+encodedKey+'" style="background:#e74c3c;color:#fff;border:none;padding:8px 16px;border-radius:6px;cursor:pointer;font-size:13px">삭제</button></div></div>';
  pop.innerHTML=html;
  pop.style.display='flex';
  document.getElementById('reg-close-btn').onclick=function(){pop.style.display='none';};
  document.getElementById('reg-del-btn').onclick=function(){delRegular(parseInt(this.dataset.rid),this.dataset.rkey);};
  pop.onclick=function(e){if(e.target===pop)pop.style.display='none';};
}
function delRegular(id,encodedKey){
  if(!confirm('이 점검 기록을 삭제하시갪니까?'))return;
  var apiBase2=curMenu==='inspection'?'/api/regular':'/api/inspections';
  fetch(apiBase2+'/'+id,{method:'DELETE'})
  .then(function(r){return r.json();}).then(function(){
    document.getElementById('reg-hist-pop').style.display='none';
    loadInspection();
  });
}
function showRemoteAbn(encodedKey){
  var k=decodeURIComponent(encodedKey);
  var p=k.split('|');
  var dist=p[0]||'',location=p[1]||'',item=p[2]||'';
  var recs=[];
  if(window._rData&&window._rData[k]) recs=window._rData[k].slice();
  recs.sort(function(a,b){return (b.check_date||'').localeCompare(a.check_date||'');});
  var abn=recs.filter(function(r){return r.status==='이상';});
  var pop=document.getElementById('rmt-abn-pop');
  if(!pop){pop=document.createElement('div');pop.id='rmt-abn-pop';pop.style.cssText='position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);z-index:5000;display:flex;align-items:center;justify-content:center';document.body.appendChild(pop);}
  var abnColor=abn.length>0?'#e74c3c':'#27ae60';
  var abnTxt=abn.length>0?'조치 '+abn.length+'건':'조치 없음';
  var detailRows='';
  recs.forEach(function(r){
    detailRows+='<tr style="border-bottom:1px solid #eee">';
    detailRows+='<td style="padding:8px 10px;font-size:12px;text-align:center">'+((r.check_date||'').slice(0,10))+'</td>';
    detailRows+='<td style="padding:8px 10px;font-size:12px">'+(r.note||'-')+'</td>';
    detailRows+='<td style="padding:8px;text-align:center;white-space:nowrap">';
    detailRows+='<button class="sra-edit-btn" data-id="'+r.id+'" data-key="'+encodedKey+'" style="background:#3498db;color:#fff;border:none;border-radius:4px;padding:4px 8px;font-size:11px;cursor:pointer;margin-right:3px">수정</button>';
    detailRows+='<button class="sra-del-btn" data-id="'+r.id+'" style="background:#e74c3c;color:#fff;border:none;border-radius:4px;padding:4px 8px;font-size:11px;cursor:pointer">삭제</button>';
    detailRows+='</td></tr>';
  });
  pop.innerHTML='<div style="background:#fff;border-radius:12px;padding:24px;width:540px;max-width:95vw;max-height:80vh;overflow-y:auto;box-shadow:0 8px 32px rgba(0,0,0,0.3)">'
    +'<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px">'
    +'<div><div style="font-size:13px;color:#666;margin-bottom:4px">'+dist+' '+location+' &gt; '+item+'</div>'
    +'<div style="font-size:26px;font-weight:900;color:'+abnColor+'">'+recs.length+'건</div>'
    +'<div style="font-size:12px;color:'+abnColor+';margin-top:2px">'+abnTxt+'</div></div>'
    +'<div style="display:flex;gap:8px;align-items:flex-start">'
    +'<button class="sra-add-btn" style="background:#27ae60;color:#fff;border:none;border-radius:6px;padding:8px 14px;font-size:12px;font-weight:700;cursor:pointer">+ 추가</button>'
    +'<button class="sra-detail-btn" style="background:#1a5276;color:#fff;border:none;border-radius:6px;padding:8px 14px;font-size:12px;font-weight:700;cursor:pointer">상세보기</button>'
    +'<button class="close-rmt-abn" style="background:#ddd;border:none;border-radius:50%;width:32px;height:32px;cursor:pointer;font-size:16px;font-weight:700">&times;</button>'
    +'</div></div>'
    +'<div class="sra-detail-panel" style="display:none">'
    +'<table style="width:100%;border-collapse:collapse"><thead><tr style="background:#1a5276;color:#fff">'
    +'<th style="padding:9px">점검일</th><th style="padding:9px">조치내용</th><th style="padding:9px">관리</th>'
    +'</tr></thead><tbody>'+detailRows+'</tbody></table></div></div>';
  pop.style.display='flex';
  pop.querySelector('.close-rmt-abn').addEventListener('click',function(){pop.style.display='none';});
  pop.querySelector('.sra-detail-btn').addEventListener('click',function(){
    var dp=pop.querySelector('.sra-detail-panel');
    var isOpen=dp.style.display!=='none';
    dp.style.display=isOpen?'none':'block';
    this.textContent=isOpen?'상세보기':'닫기';
  });
  pop.querySelector('.sra-add-btn').addEventListener('click',function(){pop.style.display='none';openRemoteInput(encodedKey);});
  pop.querySelectorAll('.sra-edit-btn').forEach(function(btn){
    btn.addEventListener('click',function(){editRemoteRec(this.dataset.id,this.dataset.key);});
  });
  pop.querySelectorAll('.sra-del-btn').forEach(function(btn){
    btn.addEventListener('click',function(){delRemoteRec(this.dataset.id,null);});
  });
}
function editRemoteRec(id,encodedKey){
  var k=encodedKey?decodeURIComponent(encodedKey):'';
  var rec=null;
  if(window._rData&&k&&window._rData[k]){
    rec=window._rData[k].find(function(r){return String(r.id)===String(id);});
  }
  var ep=document.getElementById('rmt-edit-pop');
  if(!ep){ep=document.createElement('div');ep.id='rmt-edit-pop';ep.style.cssText='position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);z-index:6000;display:flex;align-items:center;justify-content:center';document.body.appendChild(ep);}
  var dateVal=(rec&&rec.check_date?rec.check_date.slice(0,10):'');
  ep.innerHTML='<div style="background:#fff;border-radius:12px;padding:24px;width:420px;max-width:95vw;box-shadow:0 8px 32px rgba(0,0,0,0.3)">'
    +'<h3 style="font-size:15px;color:#1a5276;margin:0 0 16px">원격점검 기록 수정</h3>'
    +'<div style="margin-bottom:12px"><label style="font-size:12px;color:#555;font-weight:600">점검일</label>'
    +'<input id="re-date" type="date" value="'+dateVal+'" style="width:100%;padding:8px;border:1px solid #ddd;border-radius:6px;margin-top:4px;font-size:13px;box-sizing:border-box"></div>'
    +'<div style="margin-bottom:18px"><label style="font-size:12px;color:#555;font-weight:600">조치내용</label>'
    +'<textarea id="re-note" style="width:100%;padding:8px;border:1px solid #ddd;border-radius:6px;margin-top:4px;height:80px;resize:vertical;box-sizing:border-box;font-size:13px">'+(rec&&rec.note?rec.note:'')+'</textarea></div>'
    +'<div style="display:flex;gap:8px;justify-content:flex-end">'
    +'<button id="re-cancel" style="background:#eee;border:none;border-radius:6px;padding:9px 18px;cursor:pointer;font-size:13px">취소</button>'
    +'<button id="re-save" style="background:#1a5276;color:#fff;border:none;border-radius:6px;padding:9px 18px;cursor:pointer;font-weight:700;font-size:13px">저장</button>'
    +'</div></div>';
  ep.style.display='flex';
  ep.querySelector('#re-cancel').addEventListener('click',function(){ep.style.display='none';});
  ep.querySelector('#re-save').addEventListener('click',function(){
    var note=ep.querySelector('#re-note').value.trim();
    var dateVal=ep.querySelector('#re-date').value;
    var status=rec?rec.status:'이상';
    fetch('/api/remote/'+id,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({status:status,note:note,check_date:dateVal})})
      .then(function(r){return r.json();})
      .then(function(){
        ep.style.display='none';
        if(window._rData&&k&&window._rData[k]){
          var ri=window._rData[k].find(function(r){return String(r.id)===String(id);});
          if(ri){ri.note=note;if(dateVal)ri.check_date=dateVal+'T00:00';}
        }
        var ap=document.getElementById('rmt-abn-pop');
        var lp=document.getElementById('loc-hist-pop');
        if(ap&&ap.style.display==='flex'){showRemoteAbn(encodeURIComponent(k));}
        else if(lp&&lp.style.display==='flex'){var p=k.split('|');showLocHist(encodeURIComponent(p[0]+'|'+p[1]));}
        loadRemote();
      })
      .catch(function(e){alert('저장 실패: '+e.message);});
  });
}
function delRemoteRec(id,encodedKey){
  if(!confirm('이 기록을 삭제하시게습니까?')) return;
  fetch('/api/remote/'+id,{method:'DELETE'})
    .then(function(r){return r.json();})
    .then(function(){
      var deletedKey=null;
      if(window._rData){
        Object.keys(window._rData).forEach(function(k){
          var arr=window._rData[k];
          var idx=arr.findIndex(function(r){return String(r.id)===String(id);});
          if(idx>=0){arr.splice(idx,1);deletedKey=k;}
        });
      }
      var ap=document.getElementById('rmt-abn-pop');
      var lp=document.getElementById('loc-hist-pop');
      if(ap&&ap.style.display==='flex'&&deletedKey){
        var remaining=(window._rData[deletedKey]||[]).filter(function(r){return r.status==='이상';}).length;
        if(remaining>0){showRemoteAbn(encodeURIComponent(deletedKey));}
        else{ap.style.display='none';}
      } else if(lp&&lp.style.display==='flex'&&deletedKey){
        var p=deletedKey.split('|');
        if(p.length>=2){
          var locRem=Object.keys(window._rData||{}).some(function(k2){
            var kp=k2.split('|');
            return kp[0]===p[0]&&kp[1]===p[1]&&(window._rData[k2]||[]).some(function(r){return r.status==='이상';});
          });
          if(locRem){showLocHist(encodeURIComponent(p[0]+'|'+p[1]));}
          else{lp.style.display='none';}
        }
      } else {
        if(ap)ap.style.display='none';
        if(lp)lp.style.display='none';
      }
      loadRemote();
    })
    .catch(function(e){alert('삭제 실패: '+e.message);});
}
function addRemoteRec(encodedKey){
  var k=decodeURIComponent(encodedKey);
  var p=k.split('|');
  var dist=p[0]||'',location=p[1]||'',item=p[2]||'';
  var ap2=document.getElementById('rmt-add-pop');
  if(!ap2){ap2=document.createElement('div');ap2.id='rmt-add-pop';ap2.style.cssText='position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);z-index:6000;display:flex;align-items:center;justify-content:center';document.body.appendChild(ap2);}
  var today=new Date().toISOString().slice(0,10);
  ap2.innerHTML='<div style="background:#fff;border-radius:12px;padding:24px;width:420px;max-width:95vw;box-shadow:0 8px 32px rgba(0,0,0,0.3)">'
    +'<h3 style="font-size:15px;color:#27ae60;margin:0 0 4px">원격점검 추가</h3>'
    +'<div style="font-size:12px;color:#666;margin-bottom:16px">'+dist+' '+location+' &gt; '+item+'</div>'
    +'<div style="margin-bottom:12px"><label style="font-size:12px;color:#555;font-weight:600">점검일</label>'
    +'<input id="add-date" type="date" value="'+today+'" style="width:100%;padding:8px;border:1px solid #ddd;border-radius:6px;margin-top:4px;font-size:13px;box-sizing:border-box"></div>'
    +'<div style="margin-bottom:18px"><label style="font-size:12px;color:#555;font-weight:600">조치내용</label>'
    +'<textarea id="add-note" placeholder="조치 내용을 입력하세요..." style="width:100%;padding:8px;border:1px solid #ddd;border-radius:6px;margin-top:4px;height:80px;resize:vertical;box-sizing:border-box;font-size:13px"></textarea></div>'
    +'<div style="display:flex;gap:8px;justify-content:flex-end">'
    +'<button id="add-cancel" style="background:#eee;border:none;border-radius:6px;padding:9px 18px;cursor:pointer;font-size:13px">취소</button>'
    +'<button id="add-save" style="background:#27ae60;color:#fff;border:none;border-radius:6px;padding:9px 18px;cursor:pointer;font-weight:700;font-size:13px">저장</button>'
    +'</div></div>';
  ap2.style.display='flex';
  ap2.querySelector('#add-cancel').addEventListener('click',function(){ap2.style.display='none';});
  ap2.querySelector('#add-save').addEventListener('click',function(){
    var note=ap2.querySelector('#add-note').value.trim();
    var dateVal=ap2.querySelector('#add-date').value;
    if(!dateVal){alert('점검일을 입력하세요.');return;}
    fetch('/api/remote/save',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({key:k,check_date:dateVal+'T00:00',note:note,status:'이상',inspector:''})})
      .then(function(r){return r.json();})
      .then(function(){
        ap2.style.display='none';
        loadRemote();
        setTimeout(function(){showRemoteAbn(encodedKey);},300);
      })
      .catch(function(e){alert('저장 실패: '+e.message);});
  });
}
function showLocHist(encodedLoc){
  var loc=decodeURIComponent(encodedLoc);
  var parts=loc.split('|');
  var dist=parts[0]||'',location=parts[1]||'';
  var allAbn=[];
  if(window._remoteData){
    Object.entries(window._rData).forEach(function(kv){
      var k=kv[0],arr=kv[1];
      var p=k.split('|');
      if(p[0]===dist && p[1]===location){
        arr.forEach(function(r){
          if(r.status==='이상') allAbn.push(Object.assign({},r,{itemKey:k,item:p[2]}));
        });
      }
    });
  }
  allAbn.sort(function(a,b){return (b.check_date||'').localeCompare(a.check_date||'');});
  var rows='';
  if(allAbn.length===0){
    rows='<tr><td colspan="5" style="text-align:center;padding:20px;color:#999">이상 기록 없음</td></tr>';
  } else {
    allAbn.forEach(function(r){
      rows+='<tr style="border-bottom:1px solid #eee">';
      rows+='<td style="padding:8px 10px;font-size:12px;text-align:center">'+((r.check_date||'').slice(0,10))+'</td>';
      rows+='<td style="padding:8px 10px;font-size:12px">'+(r.item||'-')+'</td>';
      rows+='<td style="padding:8px 10px;font-size:12px;text-align:center"><span style="color:#e74c3c;font-weight:700">이상</span></td>';
      rows+='<td style="padding:8px 10px;font-size:12px">'+(r.note||'-')+'</td>';
      rows+='<td style="padding:8px;text-align:center;white-space:nowrap">';
      rows+='<button class="slh-edit-btn" data-id="'+r.id+'" data-key="'+encodeURIComponent(r.itemKey)+'" style="background:#3498db;color:#fff;border:none;border-radius:4px;padding:4px 8px;font-size:11px;cursor:pointer;margin-right:3px">수정</button>';
      rows+='<button class="slh-del-btn" data-id="'+r.id+'" style="background:#e74c3c;color:#fff;border:none;border-radius:4px;padding:4px 8px;font-size:11px;cursor:pointer">삭제</button>';
      rows+='</td></tr>';
    });
  }
  var pop=document.getElementById('loc-hist-pop');
  if(!pop){pop=document.createElement('div');pop.id='loc-hist-pop';pop.style.cssText='position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);z-index:5000;display:flex;align-items:center;justify-content:center';document.body.appendChild(pop);}
  pop.innerHTML='<div style="background:#fff;border-radius:12px;padding:24px;width:720px;max-width:95vw;max-height:80vh;overflow-y:auto;box-shadow:0 8px 32px rgba(0,0,0,0.3)">'
    +'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">'
    +'<h3 style="font-size:16px;color:#1a5276;margin:0">📍 '+dist+' '+location+' 전체 이상 현황 ('+allAbn.length+'건)</h3>'
    +'<button class="close-loc-pop" style="background:#ddd;border:none;border-radius:50%;width:32px;height:32px;cursor:pointer;font-size:16px;font-weight:700">×</button>'
    +'</div>'
    +'<table style="width:100%;border-collapse:collapse"><thead><tr style="background:#1a5276;color:#fff">'
    +'<th style="padding:9px">점검일</th><th style="padding:9px">대분류</th><th style="padding:9px">조치내용</th><th style="padding:9px">관리</th>'
    +'</tr></thead><tbody>'+rows+'</tbody></table></div>';
  pop.style.display='flex';
  pop.querySelector('.close-loc-pop').addEventListener('click',function(){pop.style.display='none';});
  pop.querySelectorAll('.slh-edit-btn').forEach(function(btn){
    btn.addEventListener('click',function(){editRemoteRec(this.dataset.id,this.dataset.key);});
  });
  pop.querySelectorAll('.slh-del-btn').forEach(function(btn){
    btn.addEventListener('click',function(){delRemoteRec(this.dataset.id,encodedLoc);});
  });
}
function editInsp(id){
  var r=null;
  if(window._maintData){Object.values(window._maintData).forEach(function(arr){arr.forEach(function(x){if(x.id==id)r=x;});});}
  var items=['패널','보드','전원','PC','카메라','스피커','마이크','입력장치','하우징','외관데코','기타'];
  var opts=items.map(function(v){return '<option value="'+v+'"'+(r&&r.item==v?' selected':'')+'>'+v+'</option>';}).join('');
  var cont=r?r.content||'':'';
  var pop=document.getElementById('edit-insp-pop');
  if(!pop){
    pop=document.createElement('div');
    pop.id='edit-insp-pop';
    pop.style.cssText='position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);z-index:9999;display:flex;align-items:center;justify-content:center';
    document.body.appendChild(pop);
  }
  pop.innerHTML='<div style="background:#fff;border-radius:12px;padding:24px;width:420px;max-width:95vw;box-shadow:0 8px 32px rgba(0,0,0,0.2)"><h3 style="margin:0 0 16px;font-size:16px;color:#1a5276">점검 내용 수정</h3><label style="font-size:13px;color:#555;display:block;margin-bottom:4px">점검 항목</label><select id="ep-item" style="width:100%;padding:8px;border:1px solid #ddd;border-radius:6px;font-size:13px;margin-bottom:12px">'+opts+'</select><label style="font-size:13px;color:#555;display:block;margin-bottom:4px">조치 사항</label><textarea id="ep-cont" style="width:100%;height:120px;padding:8px;border:1px solid #ddd;border-radius:6px;font-size:13px;resize:vertical;box-sizing:border-box">'+cont+'</textarea><div style="display:flex;gap:8px;margin-top:16px;justify-content:flex-end"><button class="ep-cancel" style="padding:8px 16px;border:1px solid #ddd;border-radius:6px;background:#fff;cursor:pointer;font-size:13px">취소</button><button class="ep-save" style="padding:8px 20px;border:none;border-radius:6px;background:#1a5276;color:#fff;cursor:pointer;font-size:13px;font-weight:600">저장</button></div></div>';
  pop.querySelector('.ep-cancel').addEventListener('click',function(){pop.style.display='none';});
  pop.querySelector('.ep-save').addEventListener('click',function(){saveEditInsp(id);});
  pop.style.display='flex';
}

function saveEditInsp(id){
  var itemEl=document.getElementById('ep-item');
  var contEl=document.getElementById('ep-cont');
  if(!itemEl||!contEl){alert('수정 오류: 입력 필드 없음');return;}
  var item=itemEl.value;
  var cont=contEl.value;
  var apiBase=curMenu==='inspection'?'/api/regular':'/api/inspections';
  fetch(apiBase+'/'+id,{
    method:'PUT',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({item:item,content:cont,status:'정상'})
  }).then(function(r){return r.json();}).then(function(d){
    try{
      if(d&&d.ok){
        var pop=document.getElementById('edit-insp-pop');
        if(pop) pop.style.display='none';
        if(window._maintData){
          Object.values(window._maintData).forEach(function(arr){
            arr.forEach(function(x){if(x.id==id){x.item=item;x.content=cont;}});
          });
        }
        var modal=document.getElementById('hist-modal');
        if(modal&&modal.classList.contains('show')&&modal.dataset.openKey){
          showHist(encodeURIComponent(modal.dataset.openKey));
        }
        alert('수정 완료!');
      } else {
        alert('수정 실패: '+JSON.stringify(d));
      }
    } catch(e){
      alert('수정 완료되었습니다.');
    }
  }).catch(function(e){
    alert('네트워크 오류: '+e.message);
  });
}

function delInsp(id,encodedKey){
  if(!confirm('이 점검 기록을 삭제하시겠습니까?'))return;
  var apiBase2=curMenu==='inspection'?'/api/regular':'/api/inspections';
  fetch(apiBase2+'/'+id,{method:'DELETE'})
  .then(function(r){return r.json();}).then(function(){
    var row=document.getElementById('irow_'+id);
    if(row)row.remove();
    loadMaintenance();
    showToast('삭제됐습니다');
  });
}
function showHist(encodedKey){
  var key=decodeURIComponent(encodedKey);
  var data=window._maintData||{};
  var recs=(data[key])||[];
  var modal=document.getElementById('hist-modal');
  if(modal) modal.dataset.openKey=key;
  var html='';
  if(recs.length===0){
    html='<p style="text-align:center;color:#999;padding:20px">이력이 없습니다</p>';
  } else {
    html+='<div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;font-size:12px">';
    html+='<thead><tr style="background:#1a5276;color:#fff">';
    html+='<th style="padding:8px 6px;white-space:nowrap;width:100px">일자</th>';
    html+='<th style="padding:8px 6px;white-space:nowrap">항목</th>';
    html+='<th style="padding:8px 6px;white-space:nowrap">점검자명</th>';
    html+='<th style="padding:8px 6px;white-space:nowrap">담당자명</th>';
    html+='<th style="padding:8px 6px;min-width:120px">조치사항</th>';
    html+='<th style="padding:8px 6px;white-space:nowrap;width:80px">사인</th>';
    html+='<th style="padding:8px 6px">사진</th>';
    html+='<th style="padding:8px 6px;white-space:nowrap">관리</th>';
    html+='</tr></thead><tbody>';
    recs.forEach(function(r){
      var signImg=r.signature ? '<img src="'+r.signature+'" style="max-height:48px;max-width:80px;object-fit:contain">' : '-';
      var imgs=[];
      try{ if(r.images) imgs=JSON.parse(r.images); } catch(e){}
      var imgsHtml='';
      imgs.forEach(function(src){
        imgsHtml+='<img src="'+src+'" style="max-height:56px;max-width:56px;object-fit:cover;border-radius:4px;margin:2px;cursor:zoom-in" onclick="openPhotoPopup(this.src)">';
      });
      if(!imgsHtml) imgsHtml='-';
      var contShort=(r.content||'').slice(0,20)+((r.content||'').length>20?'…':'');
      var contFull=(r.content||'-');
      html+='<tr id="irow_'+r.id+'" style="border-bottom:1px solid #f0f0f0">';
      html+='<td style="padding:8px 6px;text-align:center;white-space:nowrap">'+((r.created_at||'').replace('T',' ').slice(0,16))+'</td>';
      html+='<td style="padding:8px 6px;text-align:center;white-space:nowrap">'+key.split('|')[2]+'</td>';
      html+='<td style="padding:8px 6px;text-align:center;white-space:nowrap">'+((r.district||'')+' '+(r.location||'')).trim()+'</td>';
      html+='<td style="padding:8px 6px;text-align:center;white-space:nowrap">'+(r.manager||'-')+'</td>';
      html+='<td style="padding:8px 6px;cursor:pointer;color:#1a5276" onclick="showContentPopup(this)" data-full="'+contFull.replace(/"/g,'&quot;')+'">'+contShort+'</td>';
      html+='<td style="padding:8px 6px;text-align:center">'+signImg+'</td>';
      html+='<td style="padding:8px 6px;text-align:center">'+imgsHtml+'</td>';
      html+='<td style="padding:6px;text-align:center;white-space:nowrap"><button style="font-size:10px;padding:3px 8px;margin:2px;background:#1a5276;color:#fff;border:none;border-radius:4px;cursor:pointer" onclick="editInsp('+r.id+')">수정</button><br><button style="font-size:10px;padding:3px 8px;margin:2px;background:#e74c3c;color:#fff;border:none;border-radius:4px;cursor:pointer" onclick="delInsp('+r.id+')">삭제</button></td>';
      html+='</tr>';
    });
    html+='</tbody></table></div>';
  }
  document.getElementById('hist-body').innerHTML=html;
  document.getElementById('hist-modal').classList.add('show');
}
function showContentPopup(td){
  var full=td.getAttribute('data-full');
  var pop=document.getElementById('content-pop');
  if(!pop){
    pop=document.createElement('div');
    pop.id='content-pop';
    pop.style.cssText='position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.6);z-index:9998;display:flex;align-items:center;justify-content:center';
    pop.addEventListener('click',function(e){if(e.target===pop)pop.style.display='none';});
    document.body.appendChild(pop);
  }
  pop.innerHTML='<div style="background:#fff;border-radius:12px;padding:24px;max-width:480px;width:90vw;box-shadow:0 8px 32px rgba(0,0,0,0.25)"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px"><b style="font-size:15px;color:#1a5276">조치사항 전체</b><span class="scp-close" style="cursor:pointer;font-size:22px;color:#888;line-height:1">x</span></div><p style="margin:0;font-size:13px;color:#333;line-height:1.6">'+full+'</p></div>';
  pop.querySelector('.scp-close').addEventListener('click',function(){pop.style.display='none';});
  pop.style.display='flex';
}

function openPhotoPopup(src){
  var overlay=document.createElement('div');
  overlay.style.cssText='position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.85);z-index:99999;display:flex;align-items:center;justify-content:center;cursor:zoom-out';
  var img=document.createElement('img');
  img.src=src;
  img.style.cssText='max-width:90vw;max-height:90vh;object-fit:contain;border-radius:8px;box-shadow:0 4px 32px rgba(0,0,0,0.5)';
  var closeBtn=document.createElement('button');
  closeBtn.textContent='✕';
  closeBtn.style.cssText='position:absolute;top:20px;right:28px;background:none;border:none;color:#fff;font-size:32px;cursor:pointer;line-height:1;z-index:100000';
  closeBtn.onclick=function(e){e.stopPropagation();document.body.removeChild(overlay);};
  overlay.onclick=function(){document.body.removeChild(overlay);};
  img.onclick=function(e){e.stopPropagation();};
  overlay.appendChild(img);
  overlay.appendChild(closeBtn);
  document.body.appendChild(overlay);
}

function loadRemote(){
  const yr=curYear||new Date().getFullYear(),mo=String(curMonth||new Date().getMonth()+1).padStart(2,'0');
  fetch('/api/remote?year='+yr+'&month='+mo).then(function(r){return r.json();}).then(function(data){
    window._rData={};window._remoteData=data;
    Object.keys(data).forEach(function(k){
      var pts=k.split('|');if(pts.length<3)return;
      var mk=pts[0]+'|'+pts[1]+'|'+pts[2].split('>')[0];
      if(!window._rData[mk])window._rData[mk]=[];
      data[k].forEach(function(r){window._rData[mk].push(Object.assign({},r,{check_item:pts[2]}));});
    });
    var tk=Object.keys(REMOTE_TREE);
    var html='<div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;min-width:900px">';
    html+='<thead><tr style="background:#1a5276;color:#fff"><th style="min-width:180px;padding:10px;text-align:left">설치위치</th>';
    tk.forEach(function(it){html+='<th style="min-width:120px;padding:10px;font-size:12px">'+it+'</th>';});
    html+='</tr></thead><tbody>';
    Object.keys(LOCS).forEach(function(d){
      LOCS[d].forEach(function(l){
        html+='<tr><td class="loc-td" data-loc="'+d+'|'+l+'" style="padding:10px;border-bottom:1px solid #f0f0f0;cursor:pointer"><b style="font-size:12px">'+d+'</b><br><span style="font-size:12px;color:#555">'+l+'</span></td>';
        tk.forEach(function(it){
          var key=d+'|'+l+'|'+it;
          var recs=(window._rData[key])||[];
          var ab=recs.filter(function(r){return r.status==='이상';}).length;
          var col=recs.length===0?'#27ae60':(ab>0?'#e74c3c':'#27ae60');
          var lbl=recs.length===0?'정상':recs.length+'건';
          html+='<td data-key="'+key+'" data-abn="'+ab+'" data-recs="'+recs.length+'" style="text-align:center;padding:8px;border-bottom:1px solid #f0f0f0;cursor:pointer"><span style="color:'+col+';font-weight:600;font-size:12px">'+lbl+'</span></td>';
        });
        html+='</tr>';
      });
    });
    html+='</tbody></table></div>';
    document.getElementById('content').innerHTML=html;
    document.querySelectorAll('.loc-td').forEach(function(td){
      td.addEventListener('click',function(){
        var lv=this.getAttribute('data-loc');
        if(lv) showLocHist(encodeURIComponent(lv));
      });
    });
    document.querySelectorAll('[data-key]').forEach(function(td){
      td.addEventListener('click',function(){var recs2=parseInt(this.dataset.recs||0);var pp=document.getElementById('rmt-abn-pop');if(pp&&pp.style.display==='flex')return;if(recs2>0){showRemoteAbn(encodeURIComponent(this.dataset.key));}else{openRemoteInput(encodeURIComponent(this.dataset.key));}});
    });
  });
}

function openRemoteInput(encodedKey){var pp=document.getElementById("rmt-abn-pop");var pp2=document.getElementById("loc-hist-pop");if((pp&&pp.style.display==="flex")||(pp2&&pp2.style.display==="flex"))return;
  const key=decodeURIComponent(encodedKey);
  const parts=key.split('|'),d=parts[0],l=parts[1],it=parts[2];
  document.getElementById('remote-modal-title').textContent=d+' '+l+' - '+it;
  const recs=(window._rData&&window._rData[key])||[];
  let hist='';
  if(recs&&recs.length>0){
    hist='<div style="margin-bottom:12px;background:#f8f9fa;border-radius:8px;padding:10px"><div style="font-size:12px;font-weight:700;color:#555;margin-bottom:6px">📋 최근 점검이력</div>';
    recs.slice().reverse().forEach(function(r){
    hist+='<td style="padding:6px 8px;font-size:11px">'+(r.district||'')+' '+(r.location||'')+'</td>';
      if(r.check_item&&r.check_item!==it)hist+='<div style="font-size:11px;color:#1a5276;margin:2px 0">🔹 '+r.check_item+'</div>';
      hist+='<div class="hist-content">'+(r.note||'(내용없음)')+'</div></div>';
    });
    hist+='</div>';
  }
  window._rKey=key; window._rD=d; window._rL=l; window._rIt=it; window._rSub1=''; window._rSub2='';
  const tree=REMOTE_TREE[it]||{};
  const sub1s=Object.keys(tree);
  var stepHtml='';
  if(sub1s.length>0){
    stepHtml+='<div style="background:#eaf0fb;border-radius:8px;padding:10px;margin-bottom:10px">';
    stepHtml+='<div style="font-size:12px;color:#555;margin-bottom:6px;font-weight:700">① 장치 선택</div>';
    stepHtml+='<div id="r-sub1-btns" style="display:flex;flex-wrap:wrap;gap:6px">';
    sub1s.forEach(function(s){stepHtml+='<button class="cat-btn" data-v="'+s+'" onclick="rSelSub1(this)">'+s+'</button>';});
    stepHtml+='</div></div>';
    stepHtml+='<div id="r-sub2-wrap" style="display:none;background:#e8f8f5;border-radius:8px;padding:10px;margin-bottom:10px">';
    stepHtml+='<div style="font-size:12px;color:#555;margin-bottom:6px;font-weight:700">② 점검항목 선택</div>';
    stepHtml+='<div id="r-sub2-btns" style="display:flex;flex-wrap:wrap;gap:6px"></div></div>';
  }
  var actionStyle=sub1s.length>0?'display:none':'';
  var _n=new Date(),_p=function(x){return String(x).padStart(2,'0');};
  var dtLocal=_n.getFullYear()+'-'+_p(_n.getMonth()+1)+'-'+_p(_n.getDate())+'T'+_p(_n.getHours())+':'+_p(_n.getMinutes());
  stepHtml+='<div id="r-action-wrap" style="'+actionStyle+'">';
  stepHtml+='<div class="form-row"><label>점검일자</label><input type="datetime-local" id="rc-date" value="'+dtLocal+'"></div>';
  stepHtml+='<div class="form-row"><label>조치사항</label><textarea id="rc-note" placeholder="조치 내용을 입력하세요..."></textarea></div>';
  stepHtml+='<div class="form-row"><label>점검자</label><select id="rc-insp"><option value="">불러오는 중...</option></select></div>';
  stepHtml+='<div id="r-sel-path" style="font-size:12px;color:#1a5276;padding:6px 0;font-weight:600"></div>';
  stepHtml+='<button class="btn-primary" onclick="saveRemoteNew()">저장</button>';
  stepHtml+='<button class="btn-sec" style="margin-left:8px" onclick="closeModal('+String.fromCharCode(39)+'remote-modal'+String.fromCharCode(39)+')">취소</button>';
  stepHtml+='</div>';
  document.getElementById('remote-modal-body').innerHTML=hist+stepHtml;
  document.getElementById('remote-modal').classList.add('show');
  // 회원 목록 실시간 fetch
  fetch('/api/members').then(function(r){return r.json();}).then(function(members){
    var sel=document.getElementById('rc-insp');
    if(!sel)return;
    sel.innerHTML='<option value="">-- 선택 --</option>';
    members.forEach(function(m){
      var opt=document.createElement('option');
      opt.value=m.name; opt.textContent=m.name;
      sel.appendChild(opt);
    });
  }).catch(function(){
    var sel=document.getElementById('rc-insp');
    if(sel)sel.innerHTML='<option value="">-- 직접 입력 --</option>';
  });
}

function rSelSub1(btn){
  const s1=btn.getAttribute('data-v')||btn.textContent.trim();
  window._rSub1=s1; window._rSub2='';
  document.querySelectorAll('#r-sub1-btns .cat-btn').forEach(function(b){b.classList.remove('active');});
  btn.classList.add('active');
  const tree=REMOTE_TREE[window._rIt]||{};
  const sub2s=tree[s1]||[];
  if(sub2s.length===0){
    // 하위 항목 없음 → 바로 조치 입력 표시
    document.getElementById('r-sub2-wrap').style.display='none';
    document.getElementById('r-action-wrap').style.display='block';
    document.getElementById('r-sel-path').textContent='선택: '+s1;
  } else {
    let html='';
    sub2s.forEach(function(s2){html+='<button class="cat-btn" data-v="'+s2+'" onclick="rSelSub2(this)">'+s2+'</button>';});
    document.getElementById('r-sub2-btns').innerHTML=html;
    document.getElementById('r-sub2-wrap').style.display='block';
    document.getElementById('r-action-wrap').style.display='none';
    document.getElementById('r-sel-path').textContent='';
  }
}
function rSelSub2(btn){
  const s2=btn.getAttribute('data-v')||btn.textContent.trim();
  window._rSub2=s2;
  document.querySelectorAll('#r-sub2-btns .cat-btn').forEach(function(b){b.classList.remove('active');});
  btn.classList.add('active');
  document.getElementById('r-action-wrap').style.display='block';
  document.getElementById('r-sel-path').textContent='선택: '+window._rSub1+' > '+s2;
}
function saveRemoteNew(){
  const checkItem=window._rIt+(window._rSub1?'>'+window._rSub1:'')+(window._rSub2?'>'+window._rSub2:'');
  const data={district:window._rD,location:window._rL,check_item:checkItem,
    status:'이상',
    note:document.getElementById('rc-note').value,
    inspector:document.getElementById('rc-insp').value,
    check_date:document.getElementById('rc-date').value};
  fetch('/api/remote/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)})
  .then(function(r){return r.json();}).then(function(){closeModal('remote-modal');loadRemote();});
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
function printReport(){
  var yr=curYear||new Date().getFullYear();
  var mo=curMonth||new Date().getMonth()+1;
  var mnt=window._reportData||{total:0,locs:0};
  var rmt=window._reportRemote||{total:0,abnCount:0,abnormals:[]};
  var A4='width:794px;min-height:1123px;background:#fff;margin:20px auto;box-shadow:0 4px 20px rgba(0,0,0,0.3);page-break-after:always;position:relative;';
  var abRows='';
  (rmt.abnormals||[]).forEach(function(a){
    abRows+='<tr style="border-bottom:1px solid #eee">';
    abRows+='<td style="padding:5px 3px;font-size:10px;text-align:center;word-break:break-all">'+((a.check_date||'').slice(0,10))+'</td>';
    abRows+='<td style="padding:5px 4px;font-size:11px;word-break:break-all">'+a.d+' '+a.l+'</td>';
    abRows+='<td style="padding:5px 4px;font-size:11px;word-break:break-all">'+a.it+'</td>';
    abRows+='<td style="padding:5px 3px;font-size:10px;word-break:break-all;white-space:normal">'+(a.note||'-')+'</td>';
    abRows+='</tr>';
  });
  if(!abRows) abRows='<tr><td colspan="5" style="text-align:center;padding:20px;color:#999">조치 없음</td></tr>';
  var maintRows='';
  var maintRecs=[];
  if(window._maintData){Object.entries(window._maintData).forEach(function(e2){var k=e2[0],arr=e2[1];var p=k.split('|');arr.forEach(function(r){maintRecs.push({created_at:r.created_at,district:p[0],location:p[1],item:p[2],content:r.content});});});}
  maintRecs.sort(function(a,b){return (b.created_at||'').localeCompare(a.created_at||'');});
  var regRecs=[];
  if(window._regularData){Object.entries(window._regularData).forEach(function(e3){var k=e3[0],arr=e3[1];var p=k.split('|');arr.forEach(function(r){regRecs.push({created_at:r.created_at,district:p[0],location:p[1],manager:r.manager||r.inspector,signature:r.signature,images:r.images});});});}
  regRecs.sort(function(a,b){return (b.created_at||'').localeCompare(a.created_at||'');});
  var regRows='';
  regRecs.forEach(function(r){
    regRows+='<tr style="border-bottom:1px solid #eee">';
    regRows+='<td style="padding:6px 8px;font-size:11px;text-align:center">'+((r.created_at||'').slice(0,10))+'</td>';
    regRows+='<td style="padding:6px 8px;font-size:11px">'+(r.district||'')+' '+(r.location||'')+'</td>';
    regRows+='<td style="padding:6px 8px;font-size:11px;text-align:center">'+(r.manager||r.inspector||'-')+'</td>';
    regRows+='<td style="padding:6px 8px;text-align:center">'+(r.signature?'<img src="'+r.signature+'" style="max-height:40px;max-width:100px">':'-')+'</td>';
    regRows+='</tr>';
  });
  if(!regRows)regRows='<tr><td colspan="4" style="text-align:center;padding:20px;color:#999">점검 데이터 없음</td></tr>';

  maintRecs.slice(0,20).forEach(function(r){
    maintRows+='<tr style="border-bottom:1px solid #eee">';
    maintRows+='<td style="padding:6px 8px;font-size:11px;text-align:center">'+((r.created_at||'').slice(0,10))+'</td>';
    maintRows+='<td style="padding:6px 8px;font-size:11px">'+(r.district||'')+' '+(r.location||'')+'</td>';
    maintRows+='<td style="padding:6px 8px;font-size:11px">'+(r.item||'-')+'</td>';

    maintRows+='<td style="padding:6px 8px;font-size:11px">'+(r.content||'-').slice(0,30)+'</td>';
    maintRows+='</tr>';
  });
  var pop=document.getElementById('print-preview-pop');
  if(!pop){pop=document.createElement('div');pop.id='print-preview-pop';pop.style.cssText='position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.8);z-index:10000;display:flex;flex-direction:column;align-items:center;overflow-y:auto;padding-bottom:40px';document.body.appendChild(pop);}
  var moStr=String(mo).padStart(2,'0');
  var imgUrl='https://raw.githubusercontent.com/kepler8350/metadoor-inspection/main/%EC%A0%90%EA%B2%80%EB%B3%B4%EA%B3%A0%EC%84%9C001.jpg';
  pop.innerHTML=
    '<div id="pp-toolbar" style="position:sticky;top:0;z-index:1;background:rgba(15,30,50,0.95);width:100%;display:flex;justify-content:space-between;align-items:center;padding:10px 24px;box-sizing:border-box;box-shadow:0 2px 10px rgba(0,0,0,0.5)">'+
    '<span style="color:#fff;font-size:14px;font-weight:700">보고서 미리보기  '+yr+'년 '+mo+'월</span>'+
    '<div style="display:flex;gap:10px">'+
    '<button id="pp-pdf-btn" style="background:#1a5276;color:#fff;border:none;border-radius:6px;padding:9px 20px;cursor:pointer;font-size:13px;font-weight:700">PDF 저장</button>'+
    '<button id="pp-close-btn" style="background:#555;color:#fff;border:none;border-radius:6px;padding:9px 16px;cursor:pointer;font-size:13px">x 닫기</button>'+
    '</div></div>'+
    '<div id="pp-pages">'+
    '<div style="'+A4+'overflow:hidden">'+
    '<img src="'+imgUrl+'" style="width:100%;height:100%;object-fit:cover">'+
    '<div style="position:absolute;top:14.5%;left:57%;transform:translateX(-50%);font-size:18px;font-weight:900;color:#000">'+mo+'</div>'+
    '</div>'+
    '<div style="'+A4+'padding:60px 50px;box-sizing:border-box;font-family:sans-serif">'+
    '<div style="border-bottom:3px solid #1a5276;padding-bottom:12px;margin-bottom:28px">'+
    '<h1 style="font-size:24px;color:#1a5276;margin:0 0 6px">MetaDoor 유지보수 점검 보고서</h1>'+
    '<p style="color:#666;font-size:13px;margin:0">'+yr+'년 '+mo+'월 | 부산광역시 메타도어 점검 현황</p></div>'+
    '<h2 style="font-size:15px;color:#1a5276;border-left:4px solid #1a5276;padding-left:10px;margin-bottom:14px">종합 현황</h2>'+
    '<div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:14px;margin-bottom:28px">'+
    '<div style="background:#f0f8ff;border:1px solid #cde;border-radius:8px;padding:14px;text-align:center"><div style="font-size:26px;font-weight:700;color:#1a5276">'+(mnt.total||0)+'<span style="font-size:12px">건</span></div><div style="font-size:11px;color:#555;margin-top:3px">유지보수 점검</div></div>'+
    '<div style="background:#f0fff4;border:1px solid #c3e6cb;border-radius:8px;padding:14px;text-align:center"><div style="font-size:26px;font-weight:700;color:#27ae60">'+(mnt.locs||0)+'<span style="font-size:12px">곳</span></div><div style="font-size:11px;color:#555;margin-top:3px">점검 위치</div></div>'+
    '<div style="background:#fff8f0;border:1px solid #f5d5a0;border-radius:8px;padding:14px;text-align:center"><div style="font-size:26px;font-weight:700;color:#e67e22">'+(rmt.total||0)+'<span style="font-size:12px">건</span></div><div style="font-size:11px;color:#555;margin-top:3px">원격점검</div></div>'+
    '<div style="background:#fff0f0;border:1px solid #f5c0c0;border-radius:8px;padding:14px;text-align:center"><div style="font-size:26px;font-weight:700;color:#e74c3c">'+(rmt.abnCount||0)+'<span style="font-size:12px">건</span></div><div style="font-size:11px;color:#555;margin-top:3px">원격 이상</div></div>'+
    '</div>'+
    '<h2 style="font-size:15px;color:#1a5276;border-left:4px solid #1a5276;padding-left:10px;margin-bottom:12px">방문점검 이력 (총 '+maintRecs.length+'건)</h2>'+
    '<table style="width:100%;border-collapse:collapse;font-size:12px">'+
    '<thead><tr style="background:#1a5276;color:#fff"><th style="padding:8px">점검일</th><th style="padding:8px">설치위치</th><th style="padding:8px">대분류</th><th style="padding:8px">조치내용</th></tr></thead>'+
    '<tbody>'+maintRows+'</tbody></table>'+
    '</div>'+
    '<div style="'+A4+'padding:60px 50px;box-sizing:border-box;font-family:sans-serif">'+
    '<div style="border-bottom:3px solid #e74c3c;padding-bottom:12px;margin-bottom:28px">'+
    '<h1 style="font-size:24px;color:#e74c3c;margin:0 0 6px">원격점검 조치 현황</h1>'+
    '<p style="color:#666;font-size:13px;margin:0">'+yr+'년 '+mo+'월 | 이상 발생 항목 상세</p></div>'+
    '<table style="width:100%;border-collapse:collapse;font-size:12px;table-layout:fixed">'+
    '<thead><tr style="background:#1a5276;color:#fff"><th style="padding:6px 4px;width:13%;word-break:break-all">점검일</th><th style="padding:6px 4px;width:20%;word-break:break-all">설치위치</th><th style="padding:6px 4px;width:20%;word-break:break-all">대분류</th><th style="padding:6px 4px;width:47%">조치내용</th></tr></thead>'+    '<tbody>'+abRows+'</tbody></table>'+
    '<div style="position:absolute;bottom:40px;right:50px;text-align:right;font-size:11px;color:#bbb">MetaDoor 점검 시스템 | '+yr+'.'+moStr+'</div>'+
    '</div>'+
    '<div style="'+A4+'padding:60px 50px;box-sizing:border-box;font-family:sans-serif">'+
    '<div style="border-bottom:3px solid #27ae60;padding-bottom:12px;margin-bottom:28px">'+
    '<h1 style="font-size:24px;color:#27ae60;margin:0 0 6px">정기점검 현황</h1>'+
    '<p style="color:#666;font-size:13px;margin:0">'+yr+'년 '+mo+'월 | 정기방문점검 현황</p></div>'+
    '<table style="width:100%;border-collapse:collapse;font-size:12px">'+
    '<thead><tr style="background:#27ae60;color:#fff">'+
    '<th style="padding:8px;text-align:center;width:15%">점검일</th>'+
    '<th style="padding:8px;text-align:center;width:35%">설치위치</th>'+
    '<th style="padding:8px;text-align:center;width:20%">담당자</th>'+
    '<th style="padding:8px;text-align:center;width:30%">서명</th></tr></thead>'+
    '<tbody>'+regRows+'</tbody></table>'+
    '</div>'+
    '</div>';
  pop.style.display='flex';
  document.getElementById('pp-close-btn').addEventListener('click',function(){pop.style.display='none';});
  document.getElementById('pp-pdf-btn').addEventListener('click',function(){var sb=document.querySelector('.sidebar');if(sb)sb.style.display='none';
    var toolbar=document.getElementById('pp-toolbar');
    toolbar.style.display='none';
    pop.style.background='white';
    pop.style.overflow='visible';
    pop.style.position='static';
    document.body.style.overflow='visible';
    window.print();
    setTimeout(function(){toolbar.style.display='flex';pop.style.background='rgba(0,0,0,0.8)';pop.style.overflow='auto';pop.style.position='fixed';document.body.style.overflow='';},1000);
  });
}

function loadReport(){
  var yr=curYear||new Date().getFullYear();
  var mo=curMonth||(new Date().getMonth()+1);
  function card(icon,label,val,color){
    return '<div style="background:#fff;border:1px solid #e0e0e0;border-radius:10px;padding:16px 20px;display:flex;align-items:center;gap:14px">'+
      '<span style="font-size:28px">'+icon+'</span>'+
      '<div><div style="font-size:22px;font-weight:700;color:'+color+'">'+val+'</div>'+
      '<div style="font-size:12px;color:#666;margin-top:2px">'+label+'</div></div></div>';
  }
  document.getElementById('content').innerHTML='<p style="padding:20px;color:#999">데이터 로딩 중...</p>';
  Promise.all([
    fetch('/api/maintenance?year='+yr+'&month='+mo).then(function(r){return r.json();}),
    fetch('/api/remote?year='+yr+'&month='+mo).then(function(r){return r.json();}),
    fetch('/api/regular?year='+yr+'&month='+mo).then(function(r){return r.json();})
  ]).then(function(results){
    var mData=results[0]||{};
    var rData=results[1]||{};
    var regData=results[2]||{};
    window._regularData=regData;
    var mTotal=0;
    var mLocs=new Set();
    var mItems={};
    Object.keys(mData).forEach(function(k){
      var p=k.split('|');
      mLocs.add(p[0]+'|'+p[1]);
      mTotal+=(mData[k]||[]).length;
      if(!mItems[p[2]])mItems[p[2]]=0;
      mItems[p[2]]+=(mData[k]||[]).length;
    });
    var rTotal=0,rAbnCount=0;
    var abnormals=[];
    Object.keys(rData).forEach(function(k){
      (rData[k]||[]).forEach(function(r){
        if(r.status==='이상'){
        rTotal++;
          rAbnCount++;
          var p=k.split('|');
          abnormals.push({d:p[0],l:p[1],it:p[2],note:r.note,check_date:r.check_date,status:r.status});
        }
      });
    });
    window._reportData={total:mTotal,locs:mLocs.size};
    window._reportRemote={total:rTotal,abnCount:rAbnCount,abnormals:abnormals};
    window._maintData=mData;
    var html='<div style="padding:8px 0 16px">';
    html+='<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">';
    html+='<div><h2 style="font-size:20px;font-weight:700;color:#1a5276;margin:0">'+yr+'년 '+mo+'월 점검 보고서</h2>';
    html+='<p style="font-size:12px;color:#888;margin:4px 0 0">유지보수현황 + 원격점검 통합 현황</p></div>';
    html+='<button id="rpt-print-btn" style="background:#e74c3c;color:#fff;border:none;border-radius:8px;padding:10px 22px;font-size:14px;font-weight:700;cursor:pointer">보고서 출력 (PDF)</button>';
    html+='</div>';
    html+='<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:20px">';
    html+=card('🔧','유지보수 점검',mTotal+'건','#1a5276');
    html+=card('📍','점검 설치위치',mLocs.size+'곳','#27ae60');
    html+=card('📡','원격점검 건수',rTotal+'건','#8e44ad');
    html+=card('⚠️','원격 이상 건수',rAbnCount+'건','#e74c3c');
    html+='</div>';
    html+='<div style="background:#fff;border:1px solid #e0e0e0;border-radius:10px;padding:16px;margin-bottom:16px">';
    html+='<h3 style="font-size:14px;color:#1a5276;margin:0 0 12px">🔧 방문점검 항목별 건수</h3>';
    html+='<table style="width:100%;border-collapse:collapse;font-size:13px"><thead><tr style="background:#1a5276;color:#fff"><th style="padding:10px">점검항목</th><th style="padding:10px;text-align:right">건수</th></tr></thead><tbody>';
    Object.keys(mItems).forEach(function(it){
      html+='<tr style="border-bottom:1px solid #f0f0f0"><td style="padding:10px">'+it+'</td><td style="padding:10px;text-align:right;font-weight:700;color:#1a5276">'+mItems[it]+'건</td></tr>';
    });
    html+='</tbody></table></div>';
    html+='<div style="background:#fff;border:1px solid #e0e0e0;border-radius:10px;padding:16px;margin-bottom:16px">';
    html+='<h3 style="font-size:14px;color:#1a5276;margin:0 0 12px">📡 원격점검 이상 현황</h3>';
    if(rAbnCount===0){
      html+='<p style="color:#27ae60;text-align:center;padding:20px">이상 없음 ✓</p>';
    } else {
      html+='<table style="width:100%;border-collapse:collapse;font-size:13px"><thead><tr style="background:#e74c3c;color:#fff"><th style="padding:9px">일자</th><th style="padding:9px">설치위치</th><th style="padding:9px">대분류</th><th style="padding:9px">상태</th><th style="padding:9px">조치내용</th></tr></thead><tbody>';
      abnormals.forEach(function(a){
        html+='<tr style="border-bottom:1px solid #f0f0f0"><td style="padding:8px;text-align:center">'+((a.check_date||'').slice(0,10))+'</td>';
        html+='<td style="padding:8px">'+a.d+' '+a.l+'</td>';
        html+='<td style="padding:8px">'+a.it+'</td>';
        html+='<td style="padding:8px">'+(a.note||'-')+'</td></tr>';
      });
      html+='</tbody></table>';
    }
    html+='</div></div>';
    document.getElementById('content').innerHTML=html;
    var btn=document.getElementById('rpt-print-btn');
    if(btn) btn.addEventListener('click',printReport);
  }).catch(function(e){
    document.getElementById('content').innerHTML='<p style="color:red;padding:20px">보고서 오류: '+e.message+'</p>';
  });
}

function loadMembers(){
  fetch('/api/members').then(function(r){return r.json();}).then(function(members){
    let html='<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">';
    html+='<h3 style="font-size:16px;color:#1a5276;margin:0">👥 회원 목록</h3></div>';
    html+='<div style="background:#fff;border:1px solid #e0e0e0;border-radius:10px;overflow:hidden;margin-bottom:20px">';
    html+='<table style="width:100%;border-collapse:collapse;font-size:13px"><thead><tr style="background:#1a5276;color:#fff">';
    html+='<th style="padding:10px">No</th><th>이름</th><th>아이디</th><th>비밀번호</th><th>연락처</th><th>관리</th></tr></thead><tbody>';
    members.forEach(function(m){
      html+='<tr id="mrow_'+m.id+'" style="border-bottom:1px solid #f0f0f0">';
      html+='<td style="padding:8px;text-align:center">'+m.id+'</td>';
      html+='<td style="padding:8px;text-align:center"><input id="m_name_'+m.id+'" value="'+m.name+'" style="border:1px solid #ddd;border-radius:4px;padding:4px 6px;width:80px;font-size:12px"></td>';
      html+='<td style="padding:8px;text-align:center"><input id="m_uid_'+m.id+'" value="'+m.username+'" style="border:1px solid #ddd;border-radius:4px;padding:4px 6px;width:80px;font-size:12px"></td>';
      html+='<td style="padding:8px;text-align:center"><input id="m_pw_'+m.id+'" value="'+(m.password||'')+'" style="border:1px solid #ddd;border-radius:4px;padding:4px 6px;width:70px;font-size:12px"></td>';
      html+='<td style="padding:8px;text-align:center"><input id="m_ph_'+m.id+'" value="'+(m.phone||'')+'" style="border:1px solid #ddd;border-radius:4px;padding:4px 6px;width:110px;font-size:12px"></td>';
      html+='<td style="padding:8px;text-align:center;white-space:nowrap"><button class="btn-primary" style="padding:4px 10px;font-size:12px;margin-right:4px" onclick="editMember('+m.id+')">수정</button><button class="btn-del" onclick="delMember('+m.id+')">삭제</button></td>';
      html+='</tr>';
    });
    html+='</tbody></table></div>';
    // 회원 추가 폼
    html+='<div class="card" style="background:#fff;border:1px solid #e0e0e0;border-radius:10px;padding:16px">';
    html+='<h3 style="font-size:14px;color:#1a5276;margin:0 0 12px">➕ 회원 추가</h3>';
    html+='<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:10px">';
    html+='<div><label style="font-size:12px;color:#666">이름</label><input id="m-name" placeholder="이름" style="width:100%;margin-top:4px;padding:8px;border:1px solid #ddd;border-radius:6px;font-size:13px"></div>';
    html+='<div><label style="font-size:12px;color:#666">아이디</label><input id="m-uid" placeholder="아이디" style="width:100%;margin-top:4px;padding:8px;border:1px solid #ddd;border-radius:6px;font-size:13px"></div>';
    html+='<div><label style="font-size:12px;color:#666">비밀번호</label><input id="m-pw" type="password" placeholder="비밀번호" style="width:100%;margin-top:4px;padding:8px;border:1px solid #ddd;border-radius:6px;font-size:13px"></div>';
    html+='<div><label style="font-size:12px;color:#666">연락처</label><input id="m-phone" placeholder="010-0000-0000" style="width:100%;margin-top:4px;padding:8px;border:1px solid #ddd;border-radius:6px;font-size:13px"></div>';
    html+='</div><button class="btn-primary" onclick="addMember()">회원 추가</button></div>';
    document.getElementById('content').innerHTML=html;
  });
}
function editMember(id){
  var name=document.getElementById('m_name_'+id).value.trim();
  var username=document.getElementById('m_uid_'+id).value.trim();
  var pw=document.getElementById('m_pw_'+id).value.trim();
  var phone=document.getElementById('m_ph_'+id).value.trim();
  if(!name){showToast('이름을 입력하세요');return;}
  fetch('/api/members/'+id+'/update',{method:'PUT',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({name:name,username:username,password:pw,phone:phone})})
  .then(function(r){return r.json();}).then(function(){showToast('수정됐습니다');loadMembers();});
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
        "SELECT id,district,location,item,content,status,inspector,signature,manager,images,created_at FROM inspections WHERE strftime('%Y',created_at)=? AND strftime('%m',created_at)=?",
        (str(year),str(month).zfill(2))).fetchall()
    con.close()
    data={}
    for r in rows:
        key=f"{r[1]}|{r[2]}|{r[3]}"
        if key not in data:data[key]=[]
        data[key].append({'id':r[0],'content':r[4],'status':r[5],'inspector':r[6],'signature':r[7],'manager':r[8],'images':r[9],'created_at':r[10]})
    return jsonify(data)

# API: 원격점검 조회
@app.route('/api/regular')
@login_required
def api_regular():
    init_db()
    year=request.args.get('year',datetime.now().year)
    month=request.args.get('month',datetime.now().month)
    con=sqlite3.connect(DB)
    rows=con.execute(
        "SELECT id,district,location,item,content,status,inspector,signature,manager,images,created_at FROM regular_inspections WHERE strftime('%Y',created_at)=? AND strftime('%m',created_at)=?",
        (str(year),str(month).zfill(2))).fetchall()
    con.close()
    data={}
    for r in rows:
        key=f"{r[1]}|{r[2]}|{r[3]}"
        if key not in data:data[key]=[]
        data[key].append({'id':r[0],'content':r[4],'status':r[5],'inspector':r[6],'signature':r[7],'manager':r[8],'images':r[9],'created_at':r[10]})
    return jsonify(data)

@app.route('/api/remote')
@login_required
def api_remote():
    init_db()
    year=request.args.get('year',datetime.now().year)
    month=request.args.get('month',datetime.now().month)
    con=sqlite3.connect(DB)
    rows=con.execute(
        "SELECT id,district,location,check_item,status,note,inspector,check_date,created_at FROM remote_inspections WHERE strftime('%Y',check_date)=? AND strftime('%m',check_date)=?",
        (str(year),str(month).zfill(2))).fetchall()
    con.close()
    data={}
    for r in rows:
        key=f"{r[1]}|{r[2]}|{r[3]}"
        if key not in data:data[key]=[]
        data[key].append({'id':r[0],'status':r[4],'note':r[5],'inspector':r[6],'check_date':r[7],'created_at':r[8]})
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
@app.route('/api/remote/<int:rid>',methods=['PUT'])
def update_remote(rid):
    if not session.get('admin'): return jsonify({'error':'unauthorized'}),401
    b=request.json or {}
    con=sqlite3.connect(DB); cur=con.cursor()
    cd=b.get('check_date','');cur.execute('UPDATE remote_inspections SET status=?,note=?,check_date=COALESCE(NULLIF(?,\'\'),check_date) WHERE id=?',(b.get('status','이상'),b.get('note',''),cd,rid))
    con.commit(); con.close()
    return jsonify({'ok':True})

@app.route('/api/remote/<int:rid>',methods=['DELETE'])
def delete_remote(rid):
    if not session.get('admin'): return jsonify({'error':'unauthorized'}),401
    con=sqlite3.connect(DB); cur=con.cursor()
    cur.execute('DELETE FROM remote_inspections WHERE id=?',(rid,))
    con.commit(); con.close()
    return jsonify({'ok':True})

@app.route('/api/members')
@login_required
def api_members():
    init_db()
    con=sqlite3.connect(DB)
    rows=con.execute('SELECT id,username,name,phone,plain_pw FROM members ORDER BY id DESC').fetchall()
    con.close()
    return jsonify([{'id':r[0],'username':r[1],'name':r[2],'phone':r[3],'password':r[4]or''} for r in rows])

# API: 회원 추가
@app.route('/api/members/add',methods=['POST'])
@login_required
def api_member_add():
    init_db()
    d=request.get_json(force=True)
    pw=hashlib.sha256(d.get('password','').encode()).hexdigest()
    try:
        con=sqlite3.connect(DB)
        raw_pw=d.get('password','')
        pw=hashlib.sha256(raw_pw.encode()).hexdigest()
        con.execute('INSERT INTO members(username,password,name,phone,plain_pw) VALUES(?,?,?,?,?)',
            (d.get('username',''),pw,d.get('name',''),d.get('phone',''),raw_pw))
        con.commit();con.close()
        return jsonify({'ok':True})
    except sqlite3.IntegrityError:
        return jsonify({'ok':False,'error':'이미 존재하는 아이디입니다'})

# API: 회원 삭제
@app.route('/api/members/<int:mid>/update',methods=['PUT'])
def api_member_update(mid):
    init_db()
    d=request.get_json(force=True)
    con=sqlite3.connect(DB)
    updates=[];vals=[]
    if d.get('name') is not None: updates.append('name=?');vals.append(d['name'])
    if d.get('phone') is not None: updates.append('phone=?');vals.append(d['phone'])
    if d.get('username'): updates.append('username=?');vals.append(d['username'])
    if d.get('password'):
        raw_pw=d['password'];pw=hashlib.sha256(raw_pw.encode()).hexdigest()
        updates.append('password=?');vals.append(pw)
        updates.append('plain_pw=?');vals.append(raw_pw)
    if updates:
        vals.append(mid)
        con.execute('UPDATE members SET '+','.join(updates)+' WHERE id=?',vals);con.commit()
    con.close();return jsonify({'ok':True})

@app.route('/api/inspections/<int:iid>',methods=['PUT'])
def api_inspection_update(iid):
    init_db()
    d=request.get_json(force=True)
    con=sqlite3.connect(DB)
    con.execute('UPDATE inspections SET item=?,content=?,status=? WHERE id=?',
        (d.get('item',''),d.get('content',''),d.get('status','정상'),iid))
    con.commit();con.close();return jsonify({'ok':True})

@app.route('/api/inspections/<int:iid>',methods=['DELETE'])
def api_inspection_delete(iid):
    init_db()
    con=sqlite3.connect(DB)
    con.execute('DELETE FROM inspections WHERE id=?',(iid,))
    con.commit();con.close();return jsonify({'ok':True})

@app.route('/api/regular/<int:rid>',methods=['PUT'])
def api_regular_update(rid):
    init_db()
    d=request.get_json(force=True)
    con=sqlite3.connect(DB)
    con.execute('UPDATE regular_inspections SET item=?,content=?,status=? WHERE id=?',
        (d.get('item',''),d.get('content',''),d.get('status','정상'),rid))
    con.commit();con.close()
    return jsonify({'ok':True})
@app.route('/api/regular/<int:rid>',methods=['DELETE'])
def api_regular_delete(rid):
    init_db()
    con=sqlite3.connect(DB)
    con.execute('DELETE FROM regular_inspections WHERE id=?',(rid,))
    con.commit();con.close()
    return jsonify({'ok':True})

@app.route('/api/members/<int:mid>',methods=['DELETE'])
@login_required
def api_member_del(mid):
    init_db()
    con=sqlite3.connect(DB)
    con.execute('DELETE FROM members WHERE id=?',(mid,))
    con.commit();con.close()
    return jsonify({'ok':True})

# API: 점검 저장 (모바일 앱)
@app.route('/api/user/login',methods=['POST'])
def api_user_login():
    init_db()
    d=request.get_json(force=True)
    pw=hashlib.sha256(d.get('password','').encode()).hexdigest()
    con=sqlite3.connect(DB)
    row=con.execute('SELECT username,name FROM members WHERE username=? AND password=?',
        (d.get('username',''),pw)).fetchone()
    con.close()
    if row:return jsonify({'ok':True,'name':row[1]or row[0],'username':row[0]})
    return jsonify({'ok':False,'error':'아이디 또는 비밀번호가 올바르지 않습니다'})

@app.route('/api/inspection',methods=['POST'])
def api_save():
    try:
        init_db()
        d=request.get_json(force=True)
        con=sqlite3.connect(DB)
        con.execute('INSERT INTO inspections(district,location,item,content,status,inspector,signature,manager,images) VALUES(?,?,?,?,?,?,?,?,?)',
            (d.get('district',''),d.get('location',''),d.get('item',''),d.get('content',''),d.get('status','정상'),d.get('inspector',''),d.get('signature',''),d.get('manager',''),d.get('images','')))
        con.commit();con.close()
        return jsonify({'ok':True})
    except Exception as e:
        import traceback
        return jsonify({'ok':False,'error':str(e),'trace':traceback.format_exc()}),500

@app.route('/api/regular',methods=['POST'])
def api_regular_save():
    try:
        init_db()
        d=request.get_json(force=True)
        con=sqlite3.connect(DB)
        con.execute('INSERT INTO regular_inspections(district,location,item,content,status,inspector,signature,manager,images) VALUES(?,?,?,?,?,?,?,?,?)',
            (d.get('district',''),d.get('location',''),d.get('item',''),d.get('content',''),
             d.get('status','정상'),d.get('inspector',''),d.get('signature',''),
             d.get('manager',''),d.get('images','[]')))
        con.commit();con.close()
        return jsonify({'ok':True})
    except Exception as e:
        return jsonify({'ok':False,'error':str(e)}),500

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
    H.append('<div class="pg" id="s-select" style="display:none">')
    H.append('<div class="s"><span style="color:#fff;font-size:13px;font-weight:600">점검 유형 선택</span></div>')
    H.append('<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;flex:1;gap:24px;padding:40px 30px">')
    H.append('<div style="text-align:center"><span style="font-size:48px">🚧</span><div style="font-size:18px;font-weight:700;color:#1a5276;margin-top:10px">MetaDoor 점검</div><div style="font-size:12px;color:#777;margin-top:4px">점검 유형을 선택하세요</div></div>')
    H.append('<button onclick="fn_select_regular()" style="width:100%;padding:22px;background:#1a5276;color:#fff;border:none;border-radius:16px;font-size:17px;font-weight:700;cursor:pointer;box-shadow:0 4px 15px rgba(0,0,0,0.15)">📋 정기방문점검</button>')
    H.append('<button onclick="fn_select_field()" style="width:100%;padding:22px;background:#e67e22;color:#fff;border:none;border-radius:16px;font-size:17px;font-weight:700;cursor:pointer;box-shadow:0 4px 15px rgba(0,0,0,0.15)">🔧 현장방문조치</button>')
    H.append('</div></div>')
    H.append('<div class="pg" id="s2"><div class="s"><span style="color:#fff;font-size:11px;font-weight:600">검결과 위치 선택</span><span style="color:#aaa;font-size:10px">2단계 / 3단계</span></div>')
    H.append('<div class="slp" id="sl" style="display:flex;flex:1"><div class="lft" id="dlist"></div><div class="rgt" id="llist"><span style="color:#ccc;font-size:13px">선택하세요</span></div></div></div>')
    H.append('<div class="pg" id="s3"><div class="s" style="justify-content:space-between;padding:0 12px"><button onclick="fn_back()" style="background:none;border:none;color:#fff;font-size:18px;cursor:pointer">←</button><span style="color:#fff;font-size:11px;font-weight:600" id="stitle">점검 입력</span><span style="font-size:10px;color:#aaa">3단계 / 3단계</span></div>')
    H.append('<div class="ipg" id="ipg" style="display:flex">')
    H.append('<div class="row" id="row-item"><label>점검 항목</label>')
    H.append(f'<select id="sitm"><option value="">-- 항목 선택 --</option>')
    for it in ITEMS:H.append(f'<option value="{it}">{it}</option>')
    H.append('</select></div>')
    H.append('<div class="row" id="row-action"><label>조치 내용</label><textarea id="scont" rows="3" placeholder="조치 내용을 입력하세요..."></textarea></div>')
    H.append('<div class="row"><label>담당자</label><input type="text" id="sinsp" placeholder="담당자 이름" style="margin-bottom:0"></div>')
    H.append('<div class="row"><label>서명</label><canvas id="sig" height="100"></canvas>')
    H.append('<button onclick="fn_clr()" style="margin-top:4px;padding:6px;background:#f5f5f5;border:1px solid #ddd;border-radius:6px;font-size:12px;cursor:pointer;width:100%">서명 지우기</button></div>')
    H.append('<span class="lbl" style="margin-top:14px;display:block">📷 사진 첨부 (최대 5개)</span>')
    H.append('<input type="file" id="imgInput" accept="image/*" multiple style="display:none" onchange="fn_img_add(this)">')
    H.append('<div id="img-preview" style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:8px"></div>')
    H.append('<button class="bl2" id="imgAddBtn" onclick="fn_open_img()" style="margin-top:4px">📷 사진 추가</button>')
    H.append('<button class="sbtn" onclick="fn_save()">💾 점검 저장</button></div></div>')
    H.append('<div class="toast" id="toast"></div></div>')
    H.append('<script>')
    H.append(f'const LOCS={LC},ITEMS={IT};')
    H.append('const fn_select_regular=()=>{window._inspMode="regular";document.getElementById("s-select").style.display="none";const ra=document.getElementById("row-action");if(ra)ra.style.display="none";const ri=document.getElementById("row-item");if(ri)ri.style.display="none";document.getElementById("s2").style.display="flex";fn_ld();};const fn_select_field=()=>{window._inspMode="field";document.getElementById("s-select").style.display="none";const ra=document.getElementById("row-action");if(ra)ra.style.display="";const ri2=document.getElementById("row-item");if(ri2)ri2.style.display="";document.getElementById("s2").style.display="flex";fn_ld();};')
    H.append('let selD="",selL="",selUser="",curSt="정상";')
    H.append('const fn_login=()=>{const u=document.getElementById("uid").value,p=document.getElementById("upw").value;fetch("/api/user/login",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({username:u,password:p})}).then(r=>r.json()).then(res=>{if(res.ok){selUser=res.name||res.username;document.getElementById("s1").style.display="none";document.getElementById("s-select").style.display="flex";}else showToast(res.error||"로그인 실패");});};')
    H.append('const fn_ld=()=>{const d=document.getElementById("dlist");d.innerHTML="";Object.keys(LOCS).forEach(k=>{const b=document.createElement("button");b.className="dbtn";b.textContent=k;b.onclick=()=>fn_sel(k,b);d.appendChild(b);});};')
    H.append('const fn_sel=(d,btn)=>{selD=d;document.querySelectorAll(".dbtn").forEach(b=>b.classList.remove("active"));btn.classList.add("active");const r=document.getElementById("llist");r.innerHTML="";LOCS[d].forEach(l=>{const b=document.createElement("button");b.className="lbtn";b.textContent=l;b.onclick=()=>fn_go(l);r.appendChild(b);});};')
    H.append('const fn_go=(l)=>{selL=l;_imgList=[];document.getElementById("stitle").textContent=selD+" / "+selL;document.getElementById("s2").style.display="none";document.getElementById("s3").style.display="flex";document.getElementById("sinsp").value="";requestAnimationFrame(()=>requestAnimationFrame(fn_ini_canvas));};')
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
    H.append('const fn_open_img=()=>{document.getElementById("imgInput").click();};const fn_img_add=(inp)=>{const files=Array.from(inp.files);if(_imgList.length+files.length>5){showToast("최대 5개 첨부 가능");inp.value="";return;}files.forEach(function(f){const r=new FileReader();r.onload=function(e){_imgList.push({src:e.target.result});fn_render_imgs();};r.readAsDataURL(f);});inp.value="";};const fn_render_imgs=()=>{const w=document.getElementById("img-preview");if(!w)return;w.innerHTML="";_imgList.forEach(function(img,i){const d=document.createElement("div");d.style.cssText="position:relative;display:inline-block;margin:4px";const im=document.createElement("img");im.src=img.src;im.style.cssText="width:80px;height:80px;object-fit:cover;border-radius:8px;border:1px solid #ddd";const b=document.createElement("button");b.textContent="x";b.style.cssText="position:absolute;top:-6px;right:-6px;background:#e74c3c;color:#fff;border:none;border-radius:50%;width:20px;height:20px;font-size:11px;cursor:pointer";b.onclick=function(){_imgList.splice(i,1);fn_render_imgs();};d.appendChild(im);d.appendChild(b);w.appendChild(d);});const ab=document.getElementById("imgAddBtn");if(ab)ab.style.display=_imgList.length>=5?"none":"inline-block";};')
    H.append('const fn_save=()=>{const itm=document.getElementById("sitm").value;if(!itm&&window._inspMode!=="regular"){showToast("점검 항목을 선택하세요");return;}const insp=document.getElementById("sinsp").value;if(!insp.trim()){showToast("담당자 이름을 입력하세요");return;}')
    H.append('const sigEl=document.getElementById("sig");const sigData=(sigEl&&sigEl.width>0)?sigEl.toDataURL("image/png"):"";const data={district:selD,location:selL,item:itm,content:document.getElementById("scont").value,status:"정상",inspector:selUser,manager:insp,signature:sigData,images:JSON.stringify(_imgList.map(function(x){return x.src;}))};')
    H.append('fetch((window._inspMode==="regular"?"/api/regular":"/api/inspection"),{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)})')
    H.append('.then(function(r){if(!r.ok)throw new Error(r.status);return r.json();}).then(function(d){if(!d||!d.ok){showToast("저장실패");return;}showToast("\u2705 \uc810\uac80 \uc644\ub8cc!");document.getElementById("sitm").value="";document.getElementById("scont").value="";document.getElementById("sinsp").value="";if(typeof _imgList!=="undefined")_imgList=[];if(typeof fn_render_imgs==="function")fn_render_imgs();fn_clr();}).catch(function(){showToast("\uc800\uc7a5\uc2e4\ud328. \ub2e4\uc2dc \uc2dc\ub3c4\ud558\uc138\uc694.");});};')
    H.append('window.onload=()=>{const c=document.getElementById("cl");const tick=()=>{const n=new Date();c.textContent=n.getHours()+":"+(n.getMinutes()<10?"0":"")+n.getMinutes();};tick();setInterval(tick,60000);};')
    H.append('</script></body></html>')
    return ''.join(H)

if __name__=='__main__':
    init_db()
    app.run(host='0.0.0.0',port=int(os.environ.get('PORT',5000)))
