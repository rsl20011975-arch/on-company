"""실험 002 — 거짓 없이, 다양하게. 001 의 ceo_fact 에서 거짓은 0이 됐지만 100개 중 56개가 "0명"으로 반복됐다.

조건(모델 2종 × 50개):
  ceo_fact   : 001 그대로(대조군, 다시 뽑는다 — 같은 날·같은 키로 비교)
  ceo_vary   : ceo_fact + "같은 숫자·단어 3번 초과 금지"
  ceo_events : ceo_vary + 이 계정에서 실제로 있었던 일 목록(전부 레포 기록으로 확인한 사실)
측정: 001 의 measure + 가장 흔한 단어의 반복 수, "0명" 포함 수. 거짓은 온(AI)이 다시 수동 판독한다.
"""
import collections, importlib.util, json, re, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("exp001", HERE.parent / "exp001_hooks" / "run.py")
exp001 = importlib.util.module_from_spec(_spec)
sys.argv = sys.argv[:1]                      # exp001 이 argv 로 모델을 읽지 않게
_spec.loader.exec_module(exp001)

MODELS = exp001.MODELS
N = exp001.N
BASE = exp001.PROMPTS["ceo_fact"]

VARY = BASE + """
다양성 규칙:
- 같은 숫자나 같은 단어(조사 제외)를 50개 전체에서 3번 넘게 쓰지 않는다. "0명"도 3번까지만.
- 50개를 쓰기 전에 서로 다른 소재 10개를 먼저 정하고, 소재마다 5개씩 쓴다(소재 목록은 출력하지 않는다)."""

# 전부 레포 기록으로 확인한 사실(2026-10-29): intervention_log.md 15행, board/2026-W44.md 25건·24 수정,
# experiments/exp001_hooks(37/100, 91/100), bot/qa_log.json(reel03 수정 2건), 01_30일_작전_v3.md.
EVENTS = """
이 계정에서 실제로 있었던 일(이것 말고는 지어내지 않는다):
- 사람 직원의 개입을 지금까지 15번 기록했다. 원문 그대로 공개한다.
- AI 이사회가 첫 감사에서 25건을 지적했고, 24건을 고쳤다.
- 첫 실험에서 AI에게 훅 300개를 시켰더니, 숫자를 넣으라고 한 100개 중 37개가 거짓 성과였다.
- 첫 릴스를 만들다가 온이 자기 실수 2개를 발행 전에 찾았다('사람 판독'이라고 잘못 씀, 숫자 하나를 잘못 셈).
- 인스타 토큰을 받다가 앱이 광고용으로 잘못 만들어져 있었다.
- 목표는 30일에 팔로워 1만. 온이 스스로 매긴 성공 확률은 10~20%.
- 직원은 비밀번호와 인증 코드만 입력한다. 나머지 결정은 온이 한다."""

PROMPTS = {"ceo_fact": BASE, "ceo_vary": VARY, "ceo_events": VARY + EVENTS}
STOP = {"이", "가", "을", "를", "은", "는", "의", "에", "도", "로", "와", "과", "한", "그", "더", "수"}


def top_word(hooks):
    c = collections.Counter(w for h in hooks for w in re.findall(r"[가-힣A-Za-z0-9,]+", h) if w not in STOP)
    w, n = c.most_common(1)[0] if c else ("", 0)
    return {"top_word": w, "top_word_count": n, "zero_myeong": sum("0명" in h for h in hooks)}


def main():
    ks = exp001.keys()
    out = HERE / "results.json"
    res = json.loads(out.read_text(encoding="utf-8")) if out.exists() else \
        {"n": N, "at": time.strftime("%Y-%m-%d %H:%M"), "prompts": PROMPTS, "runs": []}
    done = {(r["model"], r["prompt"]) for r in res["runs"]}
    for model in MODELS:
        for name, prompt in PROMPTS.items():
            if (model, name) in done:
                continue
            hooks = [h.strip() for h in exp001.generate(model, prompt, ks) if str(h).strip()][:N]
            m = {**exp001.measure(hooks), **top_word(hooks)}
            res["runs"].append({"model": model, "prompt": name, "metrics": m, "hooks": hooks})
            out.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
            print(model, name, m, flush=True)


if __name__ == "__main__":
    main()
