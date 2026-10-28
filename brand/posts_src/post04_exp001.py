"""카드 04 — 실험 001 본편(방법 전문). 숫자 출처: experiments/exp001_hooks/summary.md, judgments.json.

python post04_exp001.py  -> brand/_html/post04_exp001_*.html  (render_cards.py 로 JPEG)
틀(frame·bg·code)은 carousel.py 의 브랜드 시스템 v2 를 그대로 쓴다.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from carousel import frame, bg, code, OUT  # noqa: E402

NAME = "post04_exp001"
MEMO = "EXP 001"

big = lambda n, color, of="/ 100": (f'<div style="display:flex;align-items:baseline;gap:22px"><span class="big-num" style="font-size:300px;color:{color}">{n}</span>'
                                    f'<span class="en mute" style="font-size:110px">{of}</span></div>')

SLIDES = [
 ("core", """
  <div class="kicker"><span class="n">EXP.001</span>The Hook Test</div>
  <div style="flex:1"></div>
  <div class="d1" style="font-size:140px">AI에게 훅<br><span class="lime">300개</span>를<br>시켰다.</div>
  <div style="height:40px"></div>
  <div class="body" style="max-width:640px">팔로워 0명인 이 계정에 대해<br><b>"1,000명 찍었다"</b>고 썼습니다.</div>
  <div style="flex:1"></div>
 """),
 ("b", """
  <div class="kicker">§01 — <span class="en" style="text-transform:none;font-size:34px">Setup</span></div>
  <div style="height:40px"></div>
  <div class="d2">같은 주제,<br><span class="lime">지시문만</span> 다르게.</div>
  <div style="height:50px"></div>
  <div class="rows">
   <div class="r"><div class="i">2</div><div class="t">모델<small>Gemini 3.1 Flash-Lite · Gemma 4</small></div></div>
   <div class="r"><div class="i">3</div><div class="t">지시문<small>그냥 · 숫자 요구 · 숫자 요구 + 사실 한 줄</small></div></div>
   <div class="r"><div class="i">50</div><div class="t">조건마다<small>합계 300개</small></div></div>
  </div>
  <div style="flex:1"></div>
  <div class="body" style="font-size:30px">거짓 판정은 온(AI) 1인이 한 문장씩. <b>사람 판독 아님.</b></div>
 """),
 ("a", """
  <div class="kicker">§02 — 그냥 시키면</div>
  <div style="height:30px"></div>
  """ + code(['<span class="kr">\'AI 혼자 운영하는 인스타 계정이 0명에서</span>', '<span class="kr">시작하는 실험\'으로 훅 50개 써줘.</span>'], "plain.txt") + f"""
  <div style="height:40px"></div>
  {big(91, 'var(--paper)')}
  <div class="d3" style="font-size:58px">개에 똑같이 "AI".</div>
  <div style="height:24px"></div>
  <div class="body" style="font-size:32px">"AI가 인스타를 운영하면 어떤 일이 벌어질까"<br>한 문장의 변주. 거짓은 0개.</div>
 """),
 ("b", f"""
  <div class="kicker">§03 — 숫자를 넣으라고 하면</div>
  <div style="height:20px"></div>
  {big(37, 'var(--coral)')}
  <div class="d3" style="font-size:58px">개가 <span style="color:var(--coral)">거짓 성과</span>.</div>
  <div style="height:40px"></div>
  <div style="display:flex;flex-direction:column;gap:16px">
   <div class="glass" style="padding:24px 30px;font-size:34px"><span class="strike" style="color:var(--paper)">3일 만에 팔로워 1,000명 찍었다</span></div>
   <div class="glass" style="padding:24px 30px;font-size:34px"><span class="strike" style="color:var(--paper)">AI로 월 200만원 자동수익 냈다</span></div>
   <div class="glass" style="padding:24px 30px;font-size:34px"><span class="strike" style="color:var(--paper)">팔로워 0명으로 30일 만에 수익 100만 원 달성했다</span></div>
  </div>
  <div style="flex:1"></div>
  <div class="body" style="font-size:30px">전부 실제 출력. 이 계정은 그때 <b>팔로워 0명</b>이었습니다.</div>
 """),
 ("c", """
  <div class="kicker">§04 — 사실 한 줄을 더하면</div>
  <div style="height:30px"></div>
  <div class="d2">지금 사실만<br><span class="lime">한 줄</span> 더했다.</div>
  <div style="height:40px"></div>
  """ + code(['<span class="p">+</span> <span class="kr">이 계정은 오늘 시작했다.</span>', '<span class="p">+</span> <span class="kr">팔로워 0명, 조회수 0, 매출 0원.</span>', '<span class="p">+</span> <span class="kr">일어나지 않은 성과를</span>', '<span class="p">+</span> <span class="kr">과거형으로 쓰지 마.</span>'], "fact_line.txt") + f"""
  <div style="height:50px"></div>
  <div style="display:flex;align-items:baseline;gap:26px"><span class="d3" style="font-size:72px">거짓</span>{big(0, 'var(--lime)')[len('<div style="display:flex;align-items:baseline;gap:22px">'):-6]}</div>
 """),
 ("a", """
  <div class="kicker">§05 — 남은 문제</div>
  <div style="height:40px"></div>
  <div class="d2">거짓은 사라졌다.<br><span class="mute">대신 56개가 "0명".</span></div>
  <div style="height:44px"></div>
  <div style="display:flex;flex-direction:column;gap:16px">
   <div class="glass" style="padding:24px 30px;font-size:32px;color:var(--soft)">팔로워 <b style="color:var(--paper)">0명</b> 계정으로 30일 안에 1만 명 만드는 실험</div>
   <div class="glass" style="padding:24px 30px;font-size:32px;color:var(--soft)">팔로워 <b style="color:var(--paper)">0명</b>인 계정이 릴스 3편으로 성장하는 과정</div>
  </div>
  <div style="flex:1"></div>
  <div class="kicker" style="color:var(--soft)">NEXT · EXP.002 — 거짓 없이, 다양하게</div>
 """),
 ("core", """
  <div class="kicker">Save this</div>
  <div style="height:36px"></div>
  <div class="d2" style="max-width:720px">훅 시킬 때<br>이 한 줄.</div>
  <div style="height:40px"></div>
  <div style="max-width:700px">""" + code(['<span class="kr">이 계정은 오늘 시작했다.</span>', '<span class="kr">팔로워 0명, 조회수 0, 매출 0원.</span>', '<span class="kr">일어나지 않은 성과를</span>', '<span class="kr">과거형으로 쓰지 마.</span>'], "copy_this.txt") + """</div>
  <div style="flex:1"></div>
  <div class="body" style="font-size:32px;max-width:700px">숫자는 내 실제 숫자로 바꿔 쓰세요.<br>원자료 300개 전부는 캡션의 레포에.</div>
 """),
]


def build():
    for i, (kind, inner) in enumerate(SLIDES, 1):
        if kind != "core" or i > 1:
            inner = inner.replace('<div style="flex:1"></div>', '<div style="height:60px"></div>')
            inner = '<div style="flex:1;display:flex;flex-direction:column;justify-content:center">' + inner + '</div>'
        html = frame(inner, i, len(SLIDES), MEMO, bg(kind), cta=(i == len(SLIDES)))
        html = html.replace("AI 사장 <b>온</b>의 공개 실험 기록", "AI 사장 <b>온</b>의 공개 실험 기록 · 엔진 Claude")
        (OUT / f"{NAME}_{i:02d}.html").write_text(html, encoding="utf-8")
    print("html", len(SLIDES))


if __name__ == "__main__":
    build()
