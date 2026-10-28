"""python render_reel.py <reel.html> <out.mp4>  — 30fps 1080x1920 H.264 (render_reel.js 의 Python 판).

이 PC 에는 Node 용 Playwright 가 없고 Python 용(Chromium 포함)만 있다(2026-10-29 확인). 동작은 JS 판과 같다:
페이지의 window.render(t) 를 프레임마다 불러 JPEG 로 찍고 ffmpeg 로 잇는다.
"""
import shutil, subprocess, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

FPS = 30


def render(src, out):
    src, out = Path(src).resolve(), Path(out).resolve()
    tmp = out.with_name(out.stem + "_frames")
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.goto(src.as_uri())
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(300)
        total = pg.evaluate("window.TOTAL")
        n = round(total * FPS)
        for i in range(n):
            pg.evaluate("t => window.render(t)", i / FPS)
            pg.screenshot(path=str(tmp / f"f{i:05d}.jpg"), type="jpeg", quality=92)
        b.close()
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS), "-i", str(tmp / "f%05d.jpg"),
                    "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart", str(out)], check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    print("ok", out, n, "frames")


if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2])
