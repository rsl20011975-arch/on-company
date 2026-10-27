// node render_reel.js reel01.html out.mp4   (30fps, 1080x1920, H.264)
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path'); const { execFileSync } = require('child_process');
const src = path.resolve(__dirname, process.argv[2]); const out = path.resolve(process.argv[3]); const FPS = 30;
const tmp = out.replace(/\.mp4$/, '_frames'); fs.rmSync(tmp, { recursive: true, force: true }); fs.mkdirSync(tmp, { recursive: true });
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + src); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
  const total = await p.evaluate(() => window.TOTAL); const N = Math.round(total * FPS);
  for (let i = 0; i < N; i++) { await p.evaluate(t => window.render(t), i / FPS);
    await p.screenshot({ path: path.join(tmp, `f${String(i).padStart(5, '0')}.jpg`), type: 'jpeg', quality: 92 }); }
  await b.close();
  execFileSync('ffmpeg', ['-y', '-v', 'error', '-framerate', String(FPS), '-i', path.join(tmp, 'f%05d.jpg'), '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out]);
  fs.rmSync(tmp, { recursive: true, force: true }); console.log('ok', out, N, 'frames');
})();
