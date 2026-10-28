"""python render_cards.py <이름접두어>  -> posts/<이름>/<이름>_NN.jpg  (render.js 의 Python 판, JPEG q92)

이 PC 에는 Node 용 Playwright 가 없고 Python 용만 있다(2026-10-29 확인). 인스타 API 는 JPEG 만 받는다(이사회 P0 #1).
"""
import re, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

B = Path(__file__).resolve().parent
IN, OUT = B / "_html", B.parent / "posts"


def render(prefix):
    files = sorted(p for p in IN.glob(f"{prefix}*.html"))
    if not files:
        sys.exit(f"{IN} 에 {prefix}*.html 이 없다")
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350})
        for f in files:
            post = re.sub(r"_\d\d\.html$", "", f.name)
            (OUT / post).mkdir(parents=True, exist_ok=True)
            pg.goto(f.as_uri())
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(200)
            pg.screenshot(path=str(OUT / post / f.name.replace(".html", ".jpg")), type="jpeg", quality=92)
        b.close()
    print("rendered", len(files))


if __name__ == "__main__":
    render(sys.argv[1])
