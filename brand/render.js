// node render.js [filter]  -> /home/user/insta/posts/<post>/<file>.png
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const IN = path.join(__dirname, '_html'); const OUT = path.join(__dirname, '..', 'posts'); const filt = process.argv[2] || '';
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1350 } });
  for (const f of fs.readdirSync(IN).filter(x => x.endsWith('.html') && x.includes(filt)).sort()) {
    const post = f.replace(/_\d\d\.html$/, ''); fs.mkdirSync(path.join(OUT, post), { recursive: true });
    await p.goto('file://' + path.join(IN, f)); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(200);
    await p.screenshot({ path: path.join(OUT, post, f.replace('.html', '.jpg')), type: 'jpeg', quality: 92 });
  }
  await b.close(); console.log('rendered');
})();
