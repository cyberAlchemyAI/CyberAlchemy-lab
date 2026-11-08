const fs=require('fs');
const path=require('path');
const PptxGenJS=require('pptxgenjs');
const pptx=new PptxGenJS();
pptx.layout='LAYOUT_WIDE';pptx.author='CyberAlchemy Lab';pptx.subject='An introduction to the open company brain';pptx.title='CyberAlchemy Lab — An open company brain';pptx.company='CyberAlchemy Lab';pptx.lang='en-US';
pptx.theme={headFontFace:'Roboto Mono',bodyFontFace:'Roboto Mono',lang:'en-US'};
const W=13.333,H=7.5,TOTAL=11,ST=pptx.ShapeType;
const C={paper:'FDFAF3',surface:'FFFDF8',soft:'F3EBE3',ink:'241F20',muted:'6C5A59',line:'D5C7C1',accent:'B31535',dark:'21191B',darkSurface:'281E21',darkLine:'5C454A',darkMuted:'C6B1AB',pale:'FAE8E8'};
const root=__dirname,assets=path.join(root,'assets');
const ext=n=>['governance','ephemeral','authority','provenance','lifecycle'].includes(n)?'png':'jpg';
const img=n=>path.join(assets,n+'.'+ext(n));
const pages=[];let slide,items=[],dark=false;
function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;')}
function pos(o){return `left:${o.x*96}px;top:${o.y*96}px;width:${o.w*96}px;height:${o.h*96}px`}
function shape(x,y,w,h,fill,stroke=null,sw=0.8){slide.addShape(ST.rect,{x,y,w,h,line:{color:stroke||fill,transparency:stroke?0:100,width:sw},fill:{color:fill}});items.push(`<div class="box" style="${pos({x,y,w,h})};background:#${fill};${stroke?`border:${sw*96/72}px solid #${stroke};`:''}"></div>`)}
function line(x1,y1,x2,y2,color=C.line,width=0.9){slide.addShape(ST.line,{x:x1,y:y1,w:x2-x1,h:y2-y1,line:{color,width}});items.push(`<div class="line" style="left:${x1*96}px;top:${y1*96}px;width:${(x2-x1)*96}px;border-top:${width*96/72}px solid #${color}"></div>`)}
function text(t,x,y,w,h,size=18,opt={}){const color=opt.color|| (dark?C.paper:C.ink);const font=opt.font||'Roboto Mono';const bold=!!opt.bold;const valign=opt.valign||'mid';const align=opt.align||'left';const fit=opt.fit||'shrink';slide.addText(t,{x,y,w,h,fontFace:font,fontSize:size,bold,color,margin:0,valign,align,breakLine:false,fit,transparency:0,hyperlink:opt.url?{url:opt.url}:undefined,paraSpaceAfterPt:0});const dec=opt.url?'text-decoration:underline;text-underline-offset:4px;':'';items.push(`<div class="txt" style="${pos({x,y,w,h})};font-size:${size*96/72}px;color:#${color};font-weight:${bold?700:400};justify-content:${valign==='top'?'flex-start':valign==='bottom'?'flex-end':'center'};text-align:${align};${dec}">${opt.url?`<a href="${esc(opt.url)}">${esc(t).replace(/\n/g,'<br>')}</a>`:esc(t).replace(/\n/g,'<br>')}</div>`)}
function image(n,x,y,w,h){const p=img(n);slide.addImage({path:p,x,y,w,h});items.push(`<img class="photo" src="assets/${n}.${ext(n)}" style="${pos({x,y,w,h})}" alt="">`)}
function start(title,num,opt={}){dark=!!opt.dark;slide=pptx.addSlide();slide.background={color:dark?C.dark:C.paper};items=[];const edge=dark?C.darkLine:C.line;if(!opt.clean){text('CYBERALCHEMY  /  LAB',.72,.29,4,.28,10,{bold:true,color:dark?C.darkMuted:C.muted});text(String(pages.length+1).padStart(2,'0')+' / '+TOTAL,11.53,.29,1.08,.28,10,{align:'right',color:dark?C.darkMuted:C.muted});line(.72,.72,12.61,.72,edge,.7)}if(title)text(title,.72,1.05,11.9,1.18,32,{bold:true,valign:'top'});return slide}
function finish(num,opt={}){if(!opt.clean){line(.72,6.94,12.61,6.94,dark?C.darkLine:C.line,.7);text('OPEN COMPANY BRAIN  ·  LOCAL PRESENTATION',.72,7.05,6.5,.2,8.6,{color:dark?C.darkMuted:C.muted});text('cyberalchemize.com',9.1,7.05,3.5,.2,8.6,{color:dark?C.darkMuted:C.muted,align:'right'})}pages.push({number:pages.length+1,html:items.join(''),dark});}
function card(x,y,w,h,opt={}){shape(x,y,w,h,opt.fill||C.surface,opt.stroke||C.line,.7)}
function tinyLabel(t,x,y,w=4){text(t.toUpperCase(),x,y,w,.26,10,{bold:true,color:dark?C.darkMuted:C.accent})}
function link(t,x,y,w,url){text(t,x,y,w,.38,12,{bold:true,color:C.accent,url})}
function dot(x,y,r=.055,color=C.accent){slide.addShape(ST.ellipse,{x:x-r,y:y-r,w:r*2,h:r*2,line:{color},fill:{color}});items.push(`<div class="dot" style="left:${(x-r)*96}px;top:${(y-r)*96}px;width:${r*2*96}px;height:${r*2*96}px;background:#${color}"></div>`)}
function caseTag(t){tinyLabel('One campaign  /  '+t,.72,1.91,10.8)}
// Opening cover — the three governance foundations.
start('',0,{clean:true});
line(.72,.72,12.61,.72,C.line,.7);tinyLabel('Open source  /  people + AI',.72,1.03,5.7);
text('CyberAlchemy\nLab',.72,1.49,5.92,1.79,39,{bold:true,valign:'top'});
line(.72,4.11,5.83,4.11,C.accent,1.25);
text('The open company brain.',.72,4.42,5.66,.62,20,{bold:true});
text('A place for people and AI to grow knowledge with its basis intact.',.72,5.17,5.52,.87,15,{color:C.muted,valign:'top'});
text('CYBERALCHEMY LAB',.72,6.59,5.7,.29,10.5,{bold:true,color:C.accent});
const pillars=[['01','Authority','What may count, and where?'],['02','Provenance','What produced it?'],['03','Lifecycle','What can change next?']];
pillars.forEach((p,i)=>{const y=1.14+i*1.82;line(6.8,y,12.61,y,C.line,.8);text(p[0],6.82,y+.21,.65,.3,11,{bold:true,color:C.accent});text(p[1],7.53,y+.19,5.0,.66,26,{bold:true,color:C.accent});text(p[2],7.55,y+.96,4.85,.36,13.2,{color:C.muted})});
line(6.8,6.6,12.61,6.6,C.line,.8);
finish(0,{clean:true});
// 1 — introduce the campaign that carries the governance story.
start('',1,{clean:true});
line(.72,.72,12.61,.72,C.line,.7);tinyLabel('One illustrative campaign case',.72,.99,6.5);
text('Which campaign\nactually worked?',.72,1.54,6.15,1.8,35,{bold:true,valign:'top'});
text('A recorded 120 leads. B recorded 60. Both spent US$1,200. The answer depends on what “qualified” means.',.72,3.72,5.7,1.16,16.5,{valign:'top'});
shape(.72,5.48,5.21,.055,C.accent);text('Q1 · accepted for this reporting purpose',.72,5.76,5.85,.8,14.5,{bold:true,valign:'top'});
card(7.03,1.04,5.58,5.64);image('authority',7.25,1.28,5.14,3.43);tinyLabel('Meaning  /  scope  /  standing',7.3,5.04,4.91);text('Q1 can govern this comparison.',7.3,5.55,4.9,.65,14.6,{bold:true});finish(1,{clean:true});
// 2 — define Q1 before contrasting recorded and qualified counts.
start('',2);
text('Qualified = valid business email + demo request.',.72,1.05,11.9,.9,28.5,{bold:true,valign:'top'});
caseTag('Q1  /  accepted for this reporting purpose');
image('company-working',.72,2.25,6.49,4.3);
shape(7.62,2.25,4.99,4.3,C.surface,C.line,.75);
tinyLabel('Campaign A under Q1',8.03,2.72,3.9);text('120 recorded\n12 qualified',8.03,3.25,4.08,1.39,22,{bold:true,valign:'top'});
line(8.03,5.01,12.15,5.01,C.accent,1.2);text('Counting all 120 as “qualified” would change the criterion. A proposal cannot quietly replace Q1.',8.03,5.24,4.12,1.1,13.1,{color:C.muted,valign:'top'});finish(2);
// 3 — apply all three lenses to the same campaign report.
start('Three lenses, one campaign report.',3);caseTag('Q1 meaning  →  R1 report');
const lenses=[['authority','AUTHORITY','Q1 governs reporting, not budget.'],['provenance','PROVENANCE','Rows + period + method → R1.'],['lifecycle','LIFECYCLE','R1 is complete; change has a route.']];
lenses.forEach((v,i)=>{const x=.72+i*4.04;card(x,2.27,3.61,4.29);image(v[0],x+.16,2.43,3.29,2.19);tinyLabel(v[1],x+.2,4.89,3.13);line(x+.2,5.33,x+3.41,5.33,C.line,.7);text(v[2],x+.2,5.57,3.19,.72,18,{bold:true,valign:'top'})});finish(3);
// 4 — show R1's result without overclaiming its implications.
start('Under Q1, B looks stronger.',4);caseTag('R1  /  illustrative comparison');
image('campaign',.72,2.34,5.79,3.86);
card(6.85,2.34,5.76,3.86);tinyLabel('Both spent US$1,200',7.18,2.65,4.9);
text('A  120 recorded  →  12 qualified',7.18,3.15,5.05,.57,16.8,{bold:true});
line(7.18,3.94,12.23,3.94,C.line,.8);
text('B   60 recorded  →  15 qualified',7.18,4.13,5.05,.57,16.8,{bold:true});
line(7.18,4.91,12.23,4.91,C.line,.8);
text('Per qualified lead: A US$100 · B US$80',7.18,5.16,5.03,.69,13.7,{color:C.accent,bold:true});
text('R1 retains Q1, the reporting period, selected rows and method. Revenue and budget decisions need more.',.72,6.37,11.85,.42,10.6,{color:C.muted});finish(4);
// 5 — explain the unresolved problem before naming its proposed successor.
start('What if “qualified” misses the target?',5);caseTag('challenge  /  target-segment fit');
image('lifecycle',.72,2.28,5.7,3.8);
card(6.77,2.28,5.84,1.63);tinyLabel('Why the team questions Q1',7.07,2.52,4.9);text('Demo requests may miss target fit.',7.07,2.96,5.08,.61,17.4,{bold:true});
line(9.69,3.92,9.69,4.36,C.accent,1.4);dot(9.69,4.36,.06);
card(6.77,4.49,5.84,1.59);tinyLabel('Q2  /  proposed successor',7.07,4.73,4.9);text('Q1 + a recorded fit assessment.',7.07,5.17,5.08,.58,17.6,{bold:true});
text('Q2 is a candidate with no assessed counts. R1 remains 12 vs 15 under Q1.',.72,6.32,11.8,.44,11.2,{color:C.muted});finish(5);
// 6 — make the promotion path visible without promoting Q2 in the example.
start('This is how company knowledge grows.',6);caseTag('knowledge  /  growth route');
image('company-working',.72,2.25,6.27,4.18);
card(7.34,2.25,5.27,4.18);tinyLabel('A route, not automatic promotion',7.68,2.55,4.5);
text('Observe the gap in Q1',7.68,3.03,4.45,.48,17.7,{bold:true});line(7.68,3.65,12.22,3.65,C.line,.7);
text('Describe + test Q2',7.68,3.82,4.45,.48,17.7,{bold:true});line(7.68,4.45,12.22,4.45,C.line,.7);
text('Owner route + gates',7.68,4.62,4.45,.48,17.7,{bold:true});line(7.68,5.25,12.22,5.25,C.line,.7);
text('Separate later adoption',7.68,5.42,4.45,.48,17.7,{bold:true});
text('Q2 remains a candidate. Later assessment would test whether a new criterion helped.',.72,6.49,11.8,.33,10.8,{color:C.muted});finish(6);
// 7 — a fresh session receives the same case with its standing intact.
start('The agent can leave. The case stays.',7);caseTag('project state  /  next session');
image('ephemeral',.72,2.26,7.19,4.52);
shape(8.25,2.26,4.36,4.52,C.surface,C.line,.75);tinyLabel('A fresh session can recover',8.59,2.66,3.5);
text('Q1 + R1 basis',8.59,3.22,3.7,.55,19.4,{bold:true});line(8.59,3.87,12.19,3.87,C.line,.7);
text('Q2 as candidate',8.59,4.07,3.7,.55,19.4,{bold:true});line(8.59,4.73,12.19,4.73,C.line,.7);
text('Open questions',8.59,4.94,3.7,.55,19.4,{bold:true});text('Standing travels with records, not an agent’s confidence.',8.59,5.82,3.66,.78,12.4,{color:C.muted,valign:'top'});finish(7);
// 8 — lead with the software factory and its intended advantages.
start('Your software factory from the future.',8);caseTag('Craft  /  Q1 informs a software rule');
text('Describe requirements, responsibilities and workflows. A typed model and selected profiles guide construction inside the chosen architecture.',.72,2.27,11.64,.77,16.1,{valign:'top'});
const craft=[
  ['ARCHITECTURE','Keep the shape','Profiles bound roles and dependencies.'],
  ['UNDERSTANDING','Keep the why','Meaning and workflows survive change.'],
  ['ASSURANCE','End routine review','For sufficiently assured, supported paths.']
];
craft.forEach((v,i)=>{const x=.72+i*4.04;card(x,3.37,3.61,2.22);tinyLabel(v[0],x+.23,3.63,3.07);text(v[1],x+.23,4.02,3.12,.57,18,{bold:true});line(x+.23,4.73,x+3.38,4.73,C.line,.7);text(v[2],x+.23,4.92,3.12,.48,12.8,{color:C.muted,valign:'top'})});
shape(.72,5.87,11.89,.57,C.soft,C.line,.7);text('Human judgment moves to purpose, requirements, exceptions and behavior.',.96,5.98,10.9,.35,13.4,{bold:true});
text('Craft is in development / closed beta. Assurance depends on selected contracts and evidence.',.72,6.58,11.8,.29,10.4,{color:C.muted});finish(8);
// 9 — picture-led entry points.
start('Now carry the method to other work.',9);
const cases=[['campaign','Which result holds?'],['customer-reply','What should we tell the customer?'],['handoff','What did we promise?']];
cases.forEach((c,i)=>{const x=.72+i*4.04;card(x,2.29,3.61,3.99);image(c[0],x+.16,2.45,3.29,2.19);text(c[1],x+.2,4.94,3.2,1.05,19,{bold:true,valign:'top'})});finish(9);
// 10 — concise invitation.
start('',10,{clean:true});line(.72,.72,12.61,.72,C.line,.7);tinyLabel('CyberAlchemy Lab  /  open source',.72,.98,6.6);
text('Let knowledge grow\nwithout losing its roots.',.72,1.71,6.22,1.82,32,{bold:true,valign:'top'});
text('Meaning has a scope. Results keep their basis. Better versions can earn their place.',.72,4.04,5.73,.97,16.2,{color:C.muted,valign:'top'});
image('ephemeral',7.11,1.04,5.5,4.11);
shape(.72,5.81,3.66,.67,C.accent);text('EXPLORE THE LAB  ↗',.98,5.98,3.16,.32,12,{bold:true,color:'FFFFFF',url:'https://cyberalchemize.com/governance-lab-series/index.html'});
card(4.62,5.81,3.89,.67);link('READ THE GUIDE  ↗',4.87,5.98,3.38,'https://cyberalchemize.com/governance-lab-series/start-here.html');
card(8.75,5.81,3.86,.67);link('INSPECT THE SOURCE  ↗',9.0,5.98,3.37,'https://github.com/cyberAlchemyAI/CyberAlchemy-lab');
text('OPEN SOURCE  /  LAB IN DEVELOPMENT  /  CRAFT CLOSED BETA',.72,6.92,11.5,.25,9.5,{color:C.muted});finish(10,{clean:true});
// Save both editable slides and a matching local browser proof.
const css=`*{box-sizing:border-box}body{margin:0;background:#21191b;color:#241f20;font-family:'Roboto Mono','DejaVu Sans Mono',monospace}.slide{width:1280px;height:720px;position:relative;overflow:hidden;background:#FDFAF3;margin:0 auto 18px;box-shadow:0 16px 50px #0005}.slide.dark{background:#21191B}.box,.line,.txt,.photo,.dot{position:absolute}.box{z-index:1}.line{z-index:2}.photo{object-fit:cover;z-index:3}.txt{display:flex;align-items:stretch;line-height:1.27;white-space:pre-wrap;z-index:4}.txt a{color:inherit;display:block}.dot{border-radius:50%;z-index:3}.screen-nav{position:fixed;right:20px;bottom:15px;z-index:100;display:flex;gap:8px;align-items:center;background:#21191B;color:#fff;padding:8px 10px;border:1px solid #5C454A}.screen-nav button{font:14px monospace;background:#F3EBE3;border:0;color:#241F20;padding:7px 10px;cursor:pointer}.screen-nav span{min-width:55px;text-align:center;font-size:13px}body.screen .slide{display:none;transform-origin:top center}body.screen .slide.active{display:block}@media print{@page{size:13.333in 7.5in;margin:0}body{background:white}.slide,.slide.active{display:block!important;margin:0;box-shadow:none;break-after:page;page-break-after:always}.screen-nav{display:none!important}}`;
const html=`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="assets/favicon.svg"><title>CyberAlchemy Lab · Introduction</title><style>${css}</style></head><body class="screen">${pages.map(p=>`<section class="slide${p.dark?' dark':''}" aria-label="Slide ${p.number} of ${TOTAL}">${p.html}</section>`).join('')}<div class="screen-nav"><button id="prev" aria-label="Previous slide">←</button><span id="count">1 / ${TOTAL}</span><button id="next" aria-label="Next slide">→</button></div><script>const slides=[...document.querySelectorAll('.slide')];let current=0;function show(n){current=Math.max(0,Math.min(slides.length-1,n));slides.forEach((s,i)=>s.classList.toggle('active',i===current));document.getElementById('count').textContent=(current+1)+' / '+slides.length;location.hash='slide-'+(current+1)}document.getElementById('prev').onclick=()=>show(current-1);document.getElementById('next').onclick=()=>show(current+1);document.addEventListener('keydown',e=>{if(['ArrowRight','PageDown',' '].includes(e.key)){e.preventDefault();show(current+1)}if(['ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();show(current-1)}});show(Math.max(0,(Number(location.hash.replace('#slide-',''))||1)-1));</script></body></html>`;
fs.writeFileSync(path.join(root,'index.html'),html);
// A single-file presenter: image data is embedded once and resolved in the browser.
// It can be opened directly from disk, without the preview server or assets folder.
const usedAssets=[...new Set(pages.flatMap(p=>[...p.html.matchAll(/src="assets\/([^"]+)"/g)].map(m=>m[1])))];
const embeddedAssets=Object.fromEntries(usedAssets.map(name=>{
  const mime=name.endsWith('.png')?'image/png':'image/jpeg';
  return [name,`data:${mime};base64,${fs.readFileSync(path.join(assets,name)).toString('base64')}`];
}));
const presenterSlides=pages.map(p=>`<section class="slide${p.dark?' dark':''}" aria-label="Slide ${p.number} of ${TOTAL}" aria-hidden="true">${p.html.replace(/src="assets\/([^"]+)"/g,(_,name)=>`data-asset="${name}"`)}</section>`).join('');
const presenterCss=`${css}
html,body{width:100%;height:100%;overflow:hidden}
body.present{background:#21191b;touch-action:pan-y}
#stage{position:absolute;left:0;top:0;width:1280px;height:720px;transform-origin:top left;outline:none}
body.present .slide{display:none;margin:0;box-shadow:none}
body.present .slide.active{display:block}
.present-controls{position:fixed;z-index:100;left:50%;bottom:max(12px,env(safe-area-inset-bottom));transform:translateX(-50%);display:flex;align-items:center;gap:6px;padding:6px;border:1px solid #e9d7d0;background:#21191bee;color:#fff;box-shadow:0 8px 28px #0005;border-radius:8px;transition:opacity .25s ease}
.present-controls.idle{opacity:.18}
.present-controls:hover,.present-controls:focus-within{opacity:1}
.present-controls button{min-width:42px;min-height:40px;border:0;border-radius:4px;background:#f3ebe3;color:#241f20;font:600 18px 'Roboto Mono',monospace;cursor:pointer}
.present-controls button:hover,.present-controls button:focus-visible{background:#a32638;color:white;outline:2px solid white;outline-offset:2px}
.present-controls button:disabled{opacity:.42;cursor:default}
.present-controls output{min-width:68px;text-align:center;font:600 14px 'Roboto Mono',monospace}
.present-help{position:fixed;left:12px;bottom:12px;color:#fff9;background:#21191bbb;padding:5px 8px;font:11px 'Roboto Mono',monospace;border-radius:4px}
@media (pointer:coarse){.present-controls.idle{opacity:1}.present-help{display:none}}
@media (max-width:620px){.present-controls{bottom:max(8px,env(safe-area-inset-bottom))}.present-controls button{min-width:38px;min-height:38px}.present-help{display:none}}
@media print{html,body{overflow:visible;height:auto}#stage{position:static;transform:none!important;width:1280px;height:auto}body.present .slide{display:block!important;break-after:page}.present-controls,.present-help{display:none!important}}`;
const presenterScript=`const assets=${JSON.stringify(embeddedAssets)};
for(const image of document.querySelectorAll('img[data-asset]')) image.src=assets[image.dataset.asset];
const stage=document.getElementById('stage'),slides=[...document.querySelectorAll('.slide')],count=document.getElementById('count'),prev=document.getElementById('prev'),next=document.getElementById('next'),full=document.getElementById('fullscreen'),controls=document.querySelector('.present-controls');
let current=0,idleTimer,startX=null,startY=null;
function fit(){const scale=Math.min(innerWidth/1280,innerHeight/720);stage.style.transform='scale('+scale+')';stage.style.left=Math.round((innerWidth-1280*scale)/2)+'px';stage.style.top=Math.round((innerHeight-720*scale)/2)+'px'}
function show(n,updateHash=true){current=Math.max(0,Math.min(slides.length-1,n));slides.forEach((slide,i)=>{const active=i===current;slide.classList.toggle('active',active);slide.setAttribute('aria-hidden',String(!active))});count.value=(current+1)+' / '+slides.length;prev.disabled=current===0;next.disabled=current===slides.length-1;document.title='CyberAlchemy Lab · '+(current+1)+' / '+slides.length;if(updateHash&&location.hash!=='#slide-'+(current+1))history.replaceState(null,'','#slide-'+(current+1))}
function fromHash(){const n=Number(location.hash.match(/^#slide-(\\d+)$/)?.[1]||1);show(n-1,false)}
function wake(){controls.classList.remove('idle');clearTimeout(idleTimer);idleTimer=setTimeout(()=>{if(!controls.matches(':focus-within'))controls.classList.add('idle')},4000)}
prev.addEventListener('click',()=>{show(current-1);wake()});next.addEventListener('click',()=>{show(current+1);wake()});
full.addEventListener('click',async()=>{if(document.fullscreenElement)await document.exitFullscreen();else await document.documentElement.requestFullscreen();wake()});
document.addEventListener('fullscreenchange',()=>{full.textContent=document.fullscreenElement?'⤡':'⛶';full.setAttribute('aria-label',document.fullscreenElement?'Exit fullscreen':'Enter fullscreen');fit()});
document.addEventListener('keydown',event=>{if(event.altKey||event.ctrlKey||event.metaKey||event.target.closest('input,textarea,select,[contenteditable]'))return;if(event.target.closest('a,button')&&[' ','Enter'].includes(event.key))return;let target=null;if(['ArrowRight','PageDown',' ','Enter'].includes(event.key))target=current+1;else if(['ArrowLeft','PageUp','Backspace'].includes(event.key))target=current-1;else if(event.key==='Home')target=0;else if(event.key==='End')target=slides.length-1;else if(event.key.toLowerCase()==='f'){event.preventDefault();full.click();return}if(target!==null){event.preventDefault();show(target);wake()}});
document.addEventListener('touchstart',event=>{startX=event.changedTouches[0].screenX;startY=event.changedTouches[0].screenY},{passive:true});
document.addEventListener('touchend',event=>{if(startX===null)return;const dx=event.changedTouches[0].screenX-startX,dy=event.changedTouches[0].screenY-startY;if(Math.abs(dx)>50&&Math.abs(dx)>Math.abs(dy)*1.25)show(current+(dx<0?1:-1));startX=startY=null},{passive:true});
addEventListener('resize',fit);addEventListener('hashchange',fromHash);addEventListener('pointermove',wake,{passive:true});fit();fromHash();wake();`;
const favicon=`data:image/svg+xml;base64,${fs.readFileSync(path.join(assets,'favicon.svg')).toString('base64')}`;
const presenter=`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><link rel="icon" href="${favicon}"><title>CyberAlchemy Lab · Presentation</title><style>${presenterCss}</style></head><body class="present"><main id="stage" aria-label="CyberAlchemy Lab presentation">${presenterSlides}</main><nav class="present-controls" aria-label="Presentation controls"><button id="prev" type="button" aria-label="Previous slide" title="Previous slide (←)">←</button><output id="count" aria-live="polite">1 / ${TOTAL}</output><button id="next" type="button" aria-label="Next slide" title="Next slide (→)">→</button><button id="fullscreen" type="button" aria-label="Enter fullscreen" title="Fullscreen (F)">⛶</button></nav><div class="present-help">← → navigate · F fullscreen · Esc exit</div><script>${presenterScript}</script></body></html>`;
fs.writeFileSync(path.join(root,'CyberAlchemy-Lab-presentation.html'),presenter);
pptx.writeFile({fileName:path.join(root,'CyberAlchemy-Lab-introduction.pptx')}).then(()=>console.log(`Wrote ${pages.length}-slide PPTX + browser preview`));
