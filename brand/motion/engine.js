const S=document.getElementById('s');
const clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x));
const eo=x=>x>=1?1:1-Math.pow(2,-10*x);                       // expo out
const bo=x=>{const c=1.70158,c3=c+1;return 1+c3*Math.pow(x-1,3)+c*Math.pow(x-1,2)}; // back out
const eio=x=>x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2;
const p=(t,a,d)=>clamp((t-a)/d);
// 단어 마스크 리빌: 단어마다 아래에서 올라옴
function words(txt,t,start,stagger=0.07,dur=0.55,cls=''){
  return txt.split(' ').map((w,i)=>{const k=eo(p(t,start+i*stagger,dur));return `<span class="w"><span class="${cls}" style="transform:translateY(${(1-k)*110}%)">${w}</span></span>`}).join(' ');
}
function exitK(t,a,d=.35){return eio(p(t,a,d))}

function makeRender(SCENES,TOTAL){function render(T){
  // 배경: 그리드 드리프트, 코어 궤도, 글로우 숨쉬기, 그레인 지터
  const orbX=760+Math.sin(T*.6)*40, orbY=1560+Math.cos(T*.5)*40, pulse=1+.04*Math.sin(T*3.2);
  const bg=`<div class="grid2" style="transform:translate(${-(T*12)%90}px,${-(T*18)%90}px)"></div>
  <div class="glow l" style="width:1100px;height:1100px;left:${orbX-420}px;top:${orbY-550}px;opacity:${.42+.08*Math.sin(T*1.7)}"></div>
  <div class="glow v" style="width:900px;height:900px;left:-500px;top:${1500+Math.sin(T*.4)*60}px"></div>
  <div class="ring dash" style="width:900px;height:900px;left:${orbX-450}px;top:${orbY-450}px;transform:rotate(${T*14}deg)"></div>
  <div class="ring" style="width:640px;height:640px;left:${orbX-320}px;top:${orbY-320}px;transform:scale(${pulse})"></div>
  <div class="core" style="width:300px;height:300px;left:${orbX-150}px;top:${orbY-150}px;transform:scale(${pulse})"></div>`;
  const hd=`<div style="position:absolute;top:120px;left:90px;right:90px;display:flex;justify-content:space-between;font-family:var(--mono);font-size:28px;letter-spacing:.08em;color:var(--mute);z-index:5"><span style="display:flex;gap:14px;align-items:center;color:var(--paper)"><span class="live"></span>ON · AI CEO</span><span>${String(Math.floor(T)).padStart(2,'0')}:${String(Math.floor((T%1)*30)).padStart(2,'0')}</span></div>`;
  let fg='';for(const [a,b,fn] of SCENES){if(T>=a&&T<b)fg+=fn(T-a)}
  const prog=`<div style="position:absolute;top:184px;left:90px;right:90px;height:3px;background:var(--line2)"><div style="height:100%;width:${T/TOTAL*100}%;background:var(--lime)"></div></div>`;
  const grain=`<div class="grain" style="transform:translate(${(Math.sin(T*97)*40)|0}px,${(Math.cos(T*83)*40)|0}px)"></div><div class="vign"></div>`;
  S.innerHTML=bg+hd+prog+`<div style="position:absolute;inset:0;z-index:4">${fg}</div>`+grain;
}
return render}
