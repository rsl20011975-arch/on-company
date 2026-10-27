// node reel_frames.js scenes.json workdir
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const scenes = JSON.parse(fs.readFileSync(process.argv[2], 'utf8')); const work = path.resolve(process.argv[3]); fs.mkdirSync(work, { recursive: true });
const CSS = `@font-face{font-family:P;src:url('file:///root/.fonts/PretendardVariable.ttf');font-weight:100 900}
html,body{margin:0;width:1080px;height:1920px;background:#0B0B0E;font-family:P;color:#F4F3EE}
.w{width:1080px;height:1920px;display:flex;flex-direction:column;justify-content:center;padding:0 90px;box-sizing:border-box;gap:30px}
.t{font-weight:800;letter-spacing:-.035em;line-height:1.15;word-break:keep-all;white-space:pre-wrap}
.a{color:#C8FF3D}.top{position:absolute;top:140px;left:90px;font-size:34px;font-weight:600;color:#9A9A94}
.dot{display:inline-block;width:18px;height:18px;border-radius:50%;background:#C8FF3D;margin-right:14px}
.sub{font-size:44px;color:#CFCFC8;font-weight:500;line-height:1.4;word-break:keep-all}`;
(async () => {
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  for (let i = 0; i < scenes.length; i++) { const s = scenes[i];
    const h=`<html><head><meta charset=utf-8><style>${CSS}</style></head><body><div class=top><span class=dot></span>AI 사장 · 사람 직원</div>
<div class=w><div class="t ${s.accent ? 'a' : ''}" style="font-size:${s.size || 110}px">${s.text}</div>${s.sub ? '<div class=sub>' + s.sub + '</div>' : ''}</div></body></html>`; const hp=path.join(work,`s${String(i).padStart(2,'0')}.html`); fs.writeFileSync(hp,h); await pg.goto('file://'+hp);
    await pg.waitForTimeout(150); await pg.screenshot({ path: path.join(work, `s${String(i).padStart(2, '0')}.png`) }); }
  await b.close(); console.log('frames ok');
})();
