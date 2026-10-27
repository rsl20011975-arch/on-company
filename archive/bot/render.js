const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path');
const IN = '/tmp/claude-0/-home-user/faa34536-a7d8-57b4-ab3c-e350cc76ad95/scratchpad/build/html';
const OUT = '/home/user/insta/posts';
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
  for (const f of fs.readdirSync(IN).filter(x => x.endsWith('.html')).sort()) {
    const post = f.replace(/_\d\d\.html$/, '');
    fs.mkdirSync(path.join(OUT, post), { recursive: true });
    await p.goto('file://' + path.join(IN, f)); await p.waitForTimeout(150);
    await p.screenshot({ path: path.join(OUT, post, f.replace('.html', '.png')), type: 'png' });
  }
  await b.close(); console.log('rendered');
})();
