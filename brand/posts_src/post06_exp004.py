"""카드 06 — 실험 004 맞춤법 본편(저장용 목록). 숫자 출처: experiments/exp004_spelling/summary.md, results.json, results_hard.json.

python post06_exp004.py  -> brand/_html/post06_exp004_*.html  (render_cards.py 로 JPEG)
조립 방식은 post05_exp002.py 와 같다. 목록 두 장(흔히 틀리는 20 · 헷갈리는 20)이 저장할 이유다.
Gemini 어려운 판은 2026-10-30 한도로 못 돌렸다 → 5장에 GPT 만이라고 적는다. 결과가 나오면 5장을 고쳐 다시 렌더한다.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from carousel import frame, bg, code, OUT  # noqa: E402

NAME = "post06_exp004"
MEMO = "EXP 004"

big = lambda n, color, of="/ 20", size=260: (f'<span style="display:inline-flex;align-items:baseline;gap:14px"><span class="big-num" style="font-size:{size}px;color:{color}">{n}</span>'
                                             f'<span class="en mute" style="font-size:{size * 11 // 30}px">{of}</span></span>')
# 틀림 → 맞음 두 칸 표. 목록 자체가 저장 가치라 본문 80자 규칙 대신 표로 다룬다(QA 기록에 남김)
pairs = lambda ps: ('<div style="display:grid;grid-template-columns:1fr 1fr;column-gap:40px;border-top:1px solid var(--line2)">'
                    + "".join(f'<div style="display:flex;gap:16px;align-items:baseline;padding:15px 0;border-bottom:1px solid var(--line2);font-size:33px;letter-spacing:-.02em">'
                              f'<span class="strike" style="min-width:150px">{a}</span><span class="mute" style="font-size:26px">→</span><b>{b}</b></div>' for a, b in ps)
                    + "</div>")

EASY = [("되요", "돼요"), ("왠일", "웬일"), ("금새", "금세"), ("몇일", "며칠"), ("설레임", "설렘"), ("바램", "바람"), ("역활", "역할"),
        ("희안한", "희한한"), ("할께요", "할게요"), ("오랫만", "오랜만"), ("일일히", "일일이"), ("어의없다", "어이없다"), ("됬다", "됐다"),
        ("뵈요", "봬요"), ("병이 낳았다", "나았다"), ("어떻하지", "어떡하지"), ("그러던지", "그러든지"), ("문안하다", "무난하다"),
        ("할려고", "하려고"), ("되?", "돼?")]
HARD = [("답을 맞추면", "맞히면"), ("들렸다 (가는 길)", "들렀다"), ("가르켰다", "가르쳤다"), ("부장님 결제", "결재"),
        ("학생으로써", "학생으로서"), ("대화로서", "대화로써"), ("댓가", "대가"), ("동생이예요", "동생이에요"), ("있다가 전화할게", "이따가"),
        ("같애", "같아"), ("바래요", "바라요"), ("삼가해 주세요", "삼가 주세요"), ("어줍잖은", "어쭙잖은"), ("않 했다", "안 했다"),
        ("내노라하는", "내로라하는"), ("곰곰히", "곰곰이"), ("깨끗히", "깨끗이"), ("구지", "굳이"), ("뵜던", "뵀던"), ("영수증 띄어", "떼어")]

SLIDES = [
 ("core", """
  <div class="kicker"><span class="n">EXP.004</span>Spell Check ×3</div>
  <div style="flex:1"></div>
  <div class="d1" style="font-size:124px">AI 맞춤법 검사,<br>같은 질문<br><span class="lime">3번</span> 했더니.</div>
  <div style="height:40px"></div>
  <div class="body" style="max-width:700px">GPT·Gemini에 문장 30개씩.<br>저장해 둘 <b>틀리기 쉬운 맞춤법 40개</b>까지.</div>
  <div style="flex:1"></div>
 """),
 ("b", """
  <div class="kicker">§01 — <span class="en" style="text-transform:none;font-size:34px">Setup</span></div>
  <div style="height:40px"></div>
  <div class="d2">보통 쓰는<br><span class="lime">그 말</span> 그대로.</div>
  <div style="height:40px"></div>
  """ + code(['<span class="kr">아래 문장들의 맞춤법을 고쳐 줘.</span>', '<span class="kr">틀린 데가 없는 문장은 그대로 둬.</span>'], "prompt.txt") + """
  <div style="height:40px"></div>
  <div class="rows">
   <div class="r"><div class="i">30</div><div class="t">문장<small>틀린 문장 20 + 맞는 문장 10 (함정)</small></div></div>
   <div class="r"><div class="i">3</div><div class="t">회씩<small>GPT-6.1 · Gemini 3.x Flash, 같은 질문 그대로</small></div></div>
  </div>
 """),
 ("a", f"""
  <div class="kicker">§02 — 흔히 틀리는 20개</div>
  <div style="height:20px"></div>
  <div style="display:flex;align-items:baseline;gap:20px">{big(120, 'var(--lime)', of='/ 120', size=190)}</div>
  <div class="d3" style="font-size:54px">두 모델 × 3번, <span class="lime">전부 고침.</span></div>
  <div style="height:16px"></div>
  <div class="body" style="font-size:30px">맞는 문장 10개도 한 번도 안 건드렸습니다.</div>
  <div style="height:34px"></div>
  {pairs(EASY)}
 """),
 ("b", f"""
  <div class="kicker">§03 — 헷갈리는 20개로 바꾸니</div>
  <div style="height:30px"></div>
  <div style="display:flex;align-items:baseline;gap:36px">{big(18, 'var(--coral)', of='', size=190)}{big(20, 'var(--paper)', of='', size=190)}{big(19, 'var(--coral)', of='/ 20', size=190)}</div>
  <div class="d3" style="font-size:54px">같은 GPT, 같은 문장, <span style="color:var(--coral)">3번 다 다름.</span></div>
  <div style="height:40px"></div>
  <div class="rows">
   <div class="r"><div class="i">1</div><div class="t">회차 · 2개 놓침<small>있다가 저녁에 → 이따가 · 어줍잖은 → 어쭙잖은</small></div></div>
   <div class="r"><div class="i">2</div><div class="t">회차 · 0개<small>전부 고침</small></div></div>
   <div class="r"><div class="i">3</div><div class="t">회차 · 1개 놓침<small>문제를 맞추면 → 맞히면</small></div></div>
  </div>
 """),
 ("c", """
  <div class="kicker">§04 — 그래서</div>
  <div style="height:36px"></div>
  <div class="d2">놓친 문장이<br>매번 <span class="lime">달랐다.</span></div>
  <div style="height:40px"></div>
  <div class="body" style="font-size:36px">어느 두 번을 합쳐도 <b>20/20</b>.<br>세 쌍 모두 놓친 것 0개.</div>
  <div style="height:50px"></div>
  <div class="glass" style="padding:24px 30px"><div class="kicker" style="font-size:22px;color:var(--mute)">한계</div>
  <div style="font-size:30px;margin-top:10px;line-height:1.5">회차 3번 · 짧은 문장. 정답표는 온이 표준국어대사전 기준으로 만들었습니다.
  헷갈리는 판의 Gemini는 한도가 차서 아직입니다(결과는 Threads·레포).</div></div>
 """),
 ("a", f"""
  <div class="kicker">§05 — 저장용 · 헷갈리는 20개 정답</div>
  <div style="height:30px"></div>
  <div class="d3" style="font-size:58px">AI도 <span style="color:var(--coral)">한 번씩 놓친</span> 쪽.</div>
  <div style="height:34px"></div>
  {pairs(HARD)}
 """),
 ("core", """
  <div class="kicker">Save this</div>
  <div style="height:36px"></div>
  <div class="d2" style="max-width:760px">중요한 글은<br><span class="lime">두 번</span> 돌린다.</div>
  <div style="height:40px"></div>
  <div style="max-width:780px">""" + code(['<span class="kr">맞춤법 고쳐 줘. 틀린 데 없으면 그대로.</span>', '<span class="c">// 새 창에서 한 번 더</span>',
                                         '<span class="kr">두 결과가 다른 문장만 사전으로 확인</span>'], "copy_this.txt") + """</div>
  <div style="flex:1"></div>
  <div class="body" style="font-size:32px;max-width:720px">AI한테 시켜 볼 일을 댓글로 주시면<br><b>다음 실험</b>으로 돌립니다.</div>
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
