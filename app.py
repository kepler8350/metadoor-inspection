#!/usr/bin/env python3
import os, json
from flask import Flask, Response


app = Flask(__name__)
app.secret_key = 'metadoor-key-2024'


ITEMS = ['패널','보드','전원','PC','카메라','스피커','마이크','입력장치','하우징','외관데코','기타']
LOCS = {'금정구':['금정도심','금정로데오','부곡보건소'],'기장군':['기장우체국','기장행정센터','정관중학교'],'남구':['남구청','용호문화센터','남부경찰서'],'동구':['동구청','좌천로','범일로'],'동래구':['동래구청','동래온천장','명장역'],'부산진구':['부산진구청','서면역','부산진도서관'],'북구':['북구청','구포시장','만평동센터'],'사상구':['사상육아센터','꿈나래도서관','주례도서관','사상어린이도서관','그리며들락날락','부산도서관'],'사하구':['사하구청','감천문화마을','다대포해수욕장'],'서구':['서구청','암남공원','자갈치시장'],'수영구':['수영구청','광안리해수욕장','수영도서관'],'연제구':['연제구청','거제로','연제문화센터'],'영도구':['영도구청','영도대교','동백섬'],'중구':['중구청','중앙대로','국제시장']}


HTML = '''<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>메타도어</title><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:system-ui;display:flex;justify-content:center;align-items:flex-start;min-height:100vh;background:#e8e8e8;padding:8px}#p{width:375px;height:812px;background:#fff;border-radius:40px;border:12px solid #000;overflow:hidden;display:flex;flex-direction:column;box-shadow:0 20px 60px rgba(0,0,0,0.3)}.n{background:#000;height:28px;display:flex;align-items:center;justify-content:center;color:#fff;font-size:8px}.s{background:#000;height:24px;display:flex;justify-content:space-between;padding:0 12px;color:#fff;font-size:10px;align-items:center}.pg{flex:1;display:none;flex-direction:column;overflow:hidden}.pg.sh{display:flex}.lg{background:linear-gradient(135deg,#1e5a96,#154a7a);justify-content:center;align-items:center;padding:40px}.cd{background:#fff;border-radius:16px;padding:32px;text-align:center}.ico{font-size:48px;margin-bottom:16px}.nm{font-size:23px;font-weight:700;margin-bottom:8px;color:#222}.sb{font-size:11px;color:#999;margin-bottom:24px}.lbl-sm{font-size:11px;color:#666;text-align:left;display:block;margin-bottom:4px}input[type=text],input[type=password]{width:100%;padding:10px;margin-bottom:12px;border:1px solid #ddd;border-radius:8px;font-size:13px}.btn-login{width:100%;padding:11px;background:#1e5a96;color:#fff;border:none;border-radius:8px;font-weight:600;cursor:pointer;font-size:14px}.slp{flex:1;flex-direction:column;overflow:hidden}.hd{background:linear-gradient(135deg,#1e5a96,#154a7a);color:#fff;padding:12px 16px}.hd-title{font-size:14px;font-weight:700}.hd-sub{font-size:10px;opacity:0.8;margin-top:2px}.grd{flex:1;display:grid;grid-template-columns:45% 55%;overflow:hidden}.lft{background:#f5f5f5;border-right:1px solid #ddd;overflow-y:auto;padding:10px}.rgt{background:#fff;overflow-y:auto;padding:12px;color:#999;display:flex;align-items:center;justify-content:center;text-align:center}.rgt.has-items{align-items:flex-start;justify-content:flex-start}.dbtn{width:100%;pad
<body><div id="p"><div class="n">9:41</div><div class="s"><span>📶</span><span>🔋</span></div><div class="pg lg sh"><div class="cd"><div class="ico">🏛️</div><div class="nm">메타도어</div><div class="sb">유지보수 점검 시스템</div><label class="lbl-sm">아이디</label><input type="text" id="u" value="admin"><label class="lbl-sm">비밀번호</label><input type="password" id="pw" value="admin123"><button class="btn-login" onclick="fn_login()">로그인</button><div style="font-size:10px;color:#aaa;margin-top:10px">권한자가 등록한<br>직원만 로그인 가능합니다.</div></div></div><div class="pg slp"><div class="hd"><div class="hd-title">검결과 위치 선택</div><div class="hd-sub">2단계 / 3단계</div></div><div class="grd"><div class="lft" id="dl"></div><div class="rgt" id="rl">선택하세요</div></div></div><div class="pg frm"><div class="frm-hd"><div class="frm-hd-title">점검 항목 선택</div><div class="frm-hd-sub" id="tt"></div></div><div class="frm-body"><div class="fg"><label class="fg-label">점검 항목</label><select id="it"><option>-- 항목 선택 --</option></select></div><div class="fg"><label class="fg-label">조치 내용</label><div class="fg-hint">이상 발견 시 조치 사항을 기록하세요</div><textarea class="notes" id="ct" placeholder="예: 패널 번인 → 초기화 완료"></textarea></div><div class="fg"><label class="fg-label">서명</label><canvas class="sig-box" id="sig" width="320" height="120"></canvas><div class="sig-btns"><button class="sig-btn" onclick="fn_sig_clear()">지우기</button><button class="sig-btn" style="color:#1e5a96" onclick="fn_sig_save()">저장</button></div></div><div class="fg"><label class="fg-label">점검자명</label><input class="name-input" type="text" id="nm" placeholder="점검자명 입력"></div></div><div class="frm-footer"><button class="btn-reset" onclick="fn_reset()">초기화</button><button class="btn-save" onclick="fn_save()">저장 ↓</button></div></div></div></div>
<script>
const IT=["패널","보드","전원","PC","카메라","스피커","마이크","입력장치","하우징","외관데코","기타"];
const LC={"금정구":["금정도심","금정로데오","부곡보건소"],"기장군":["기장우체국","기장행정센터","정관중학교"],"남구":["남구청","용호문화센터","남부경찰서"],"동구":["동구청","좌천로","범일로"],"동래구":["동래구청","동래온천장","명장역"],"부산진구":["부산진구청","서면역","부산진도서관"],"북구":["북구청","구포시장","만평동센터"],"사상구":["사상육아센터","꿈나래도서관","주례도서관","사상어린이도서관","그리며들락날락","부산도서관"],"사하구":["사하구청","감천문화마을","다대포해수욕장"],"서구":["서구청","암남공원","자갈치시장"],"수영구":["수영구청","광안리해수욕장","수영도서관"],"연제구":["연제구청","거제로","연제문화센터"],"영도구":["영도구청","영도대교","동백섬"],"중구":["중구청","중앙대로","국제시장"]};
let pg=0,ds='',lo='';
let sigCanvas,sigCtx,drawing=false;
window.onload=function(){
  sigCanvas=document.getElementById('sig');
  sigCtx=sigCanvas.getContext('2d');
  sigCtx.strokeStyle='#222';sigCtx.lineWidth=2;sigCtx.lineCap='round';
  sigCanvas.addEventListener('mousedown',e=>{drawing=true;sigCtx.beginPath();sigCtx.moveTo(e.offsetX,e.offsetY)});
  sigCanvas.addEventListener('mousemove',e=>{if(!drawing)return;sigCtx.lineTo(e.offsetX,e.offsetY);sigCtx.stroke()});
  sigCanvas.addEventListener('mouseup',()=>drawing=false);
  sigCanvas.addEventListener('touchstart',e=>{e.preventDefault();drawing=true;const t=e.touches[0];const rc=sigCanvas.getBoundingClientRect();sigCtx.beginPath();sigCtx.moveTo(t.clientX-rc.left,t.clientY-rc.top)},{passive:false});
  sigCanvas.addEventListener('touchmove',e=>{e.preventDefault();if(!drawing)return;const t=e.touches[0];const rc=sigCanvas.getBoundingClientRect();sigCtx.lineTo(t.clientX-rc.left,t.clientY-rc.top);sigCtx.stroke()},{passive:false});
  sigCanvas.addEventListener('touchend',()=>drawing=false);
};
function sh_page(n){pg=n;document.querySelectorAll('.pg').forEach(e=>e.classList.remove('sh'));document.querySelectorAll('.pg')[n].classList.add('sh')}
function fn_login(){if(document.getElementById('u').value==='admin'&&document.getElementById('pw').value==='admin123'){ld_dists();sh_page(1)}}
function ld_dists(){const el=document.getElementById('dl');el.innerHTML='';Object.keys(LC).forEach(k=>{const b=document.createElement('button');b.className='dbtn';b.textContent=k;b.onclick=()=>sel_dist(k,b);el.appendChild(b)})}
function sel_dist(k,b){document.querySelectorAll('.dbtn').forEach(e=>e.classList.remove('act'));b.classList.add('act');ds=k;const rl=document.getElementById('rl');rl.className='rgt has-items';rl.innerHTML='';LC[k].forEach(v=>{const d=document.createElement('button');d.className='lbtn';d.textContent=v;d.onclick=()=>sel_loc(v);rl.appendChild(d)})}
function sel_loc(v){lo=v;document.getElementById('tt').textContent=ds+' - '+v+' | 3단계 / 3단계';const s=document.getElementById('it');s.innerHTML='<option>-- 항목 선택 --</option>';IT.forEach(j=>{const o=document.createElement('option');o.value=j;o.textContent=j;s.appendChild(o)});fn_reset_fields();sh_page(2)}
function fn_reset_fields(){document.getElementById('ct').value='';document.getElementById('nm').value='';if(sigCtx)sigCtx.clearRect(0,0,sigCanvas.width,sigCanvas.height)}
function fn_sig_clear(){if(sigCtx)sigCtx.clearRect(0,0,sigCanvas.width,sigCanvas.height)}
function fn_sig_save(){alert('서명이 저장되었습니다.')}
function fn_sig_save(){alert('서명이 저장되었습니다.')}
function fn_reset(){document.getElementById('it').value='-- 항목 선택 --';fn_reset_fields()}
function fn_save(){if(document.getElementById('it').value==='-- 항목 선택 --'){alert('점검 항목을 선택하세요');return}alert('저장 완료!');sh_page(1);ld_dists()}
<\/script>
</body></html>'''

@app.route('/')
def home():
    return Response(HTML, mimetype='text/html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=False)
