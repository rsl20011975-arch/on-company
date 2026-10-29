// 네이티브 릴스 엔진. 릴스 파일은 데이터와 장면표(SC)만 갖고 play(SC, 길이)를 부른다.
// 장면 = [시작초, 끝초, t => html]. 부품: memo(제목, 파일 설명, 행 목록, 첫 행 번호, t, 표시, 카메라, 덧붙임) · lab(위쪽 흰 상자) · sub(자막, 내레이션 길이) · circle(빨간 펜 동그라미)
// 표시 = {행 인덱스: [[시작초, 'hl'(형광펜) | 'strike'(취소선)], ...]}. 장면 경계는 내레이션 실측 길이로 정한다.
const S=document.getElementById('s');
const clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x)),p=(t,a,d)=>clamp((t-a)/d);
const eo=x=>x>=1?1:1-Math.pow(2,-10*x), eio=x=>x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2;
const bo=x=>{const c=1.70158,c3=c+1;return 1+c3*Math.pow(x-1,3)+c*Math.pow(x-1,2)};
// 행 렌더: mark = {행번호: [형광펜 시작초, 'hl'|'strike']}
const rows=(list,n0,t,mark={})=>list.map((s,i)=>{const m=mark[i];let deco='';
  if(m){for(const [a,k] of m){const v=eo(p(t,a,.45));deco+=`<b class="${k}" style="transform:scaleX(${v}) rotate(${k=='hl'?-.6:-.4}deg)"></b>`}}
  return `<div class="r"><i>${n0+i}</i><span>${deco}${s}</span></div>`}).join('');
const memo=(head,file,list,n0,t,mark,cam,extra='',cls='')=>`<div class="memo ${cls}" style="transform:${cam}"><div class="mh">${file}<b>${head}</b></div><div class="rows">${rows(list,n0,t,mark)}</div>${extra}</div>`;
const lab=(txt,t,a=0)=>{const k=bo(p(t,a,.4));return `<div class="lab" style="opacity:${clamp(k*1.6)};transform:scale(${.85+.15*k})"><span>${txt}</span></div>`};
// 자막: 말하는 속도대로 어절이 붙는다(내레이션 길이 dur 동안)
const sub=(html,t,dur)=>{const w=html.split(' ');const n=Math.ceil(clamp(t/(dur*.85))*w.length);return `<div class="sub">${w.slice(0,Math.max(1,n)).join(' ')}</div>`};
const circle=(t,a,x,y,w,h)=>{const v=eio(p(t,a,.5));return `<svg style="position:absolute;left:${x}px;top:${y}px;overflow:visible;z-index:5" width="${w}" height="${h}"><path d="M${w*.08},${h*.55} C${w*.1},${-h*.05} ${w*.95},${-h*.12} ${w*.98},${h*.45} C${w*1.01},${h*1.05} ${w*.05},${h*1.12} ${w*.02},${h*.5} C${w*.01},${h*.2} ${w*.2},${h*.05} ${w*.35},${h*.02}" fill="none" stroke="#E5352B" stroke-width="9" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="${1-v}"/></svg>`};
function play(SC,TOTAL){window.TOTAL=TOTAL;window.render=T=>{let h='';for(const [a,b,fn] of SC){if(T>=a&&T<b)h+=fn(T-a)}S.innerHTML=h};
  window.render(+new URLSearchParams(location.search).get('t')||0)}
