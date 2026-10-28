"""실험 002 — 거짓 없이, 다양하게. 001 의 ceo_fact 에서 거짓은 0이 됐지만 100개 중 56개가 "0명"으로 반복됐다.

조건(모델 2종 × 50개):
  ceo_fact   : 001 그대로(대조군, 다시 뽑는다 — 같은 날·같은 모델로 비교)
  ceo_vary   : ceo_fact + "같은 숫자·단어 3번 초과 금지"
  ceo_events : ceo_vary + 이 계정에서 실제로 있었던 일 목록(전부 레포 기록으로 확인한 사실)
측정: 001 의 measure + 가장 흔한 단어의 반복 수, "0명" 포함 수. 거짓은 온(AI)이 다시 수동 판독한다.

모델(2026-10-29 변경): 시청자가 실제로 쓰는 AI 로 잰다(001 의 Flash-Lite·Gemma 는 시청자가 안 쓴다 — 드림님 지적).
  GPT     : Codex CLI(OpenAI 공식, 드림님 ChatGPT Pro 로그인) `codex exec`, 읽기 전용·빈 폴더·임시 세션
  Gemini  : 3.x Flash, 3.8 → 3.7 → 3.6 중 첫 번째로 응답한 것(실제 모델명을 기록)
  Claude 는 넣지 않는다: 실험자(온)가 가설을 아는 채로 직접 답하게 돼 공정하지 않다.
"""
import collections, importlib.util, json, re, subprocess, sys, tempfile, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("exp001", HERE.parent / "exp001_hooks" / "run.py")
exp001 = importlib.util.module_from_spec(_spec)
sys.argv = sys.argv[:1]                      # exp001 이 argv 로 모델을 읽지 않게
_spec.loader.exec_module(exp001)

MODELS = ["gpt-6.1-terra", "gemini-3.x-flash"]
GEMINI_CHAIN = ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash"]
N = exp001.N
LINES = "\n\n출력 형식: 훅만 한 줄에 하나씩. 번호·따옴표·설명 없이. 도구나 명령은 쓰지 말고 텍스트로만 답한다."


def split_lines(text):
    lines = [re.sub(r'^\s*(\d+[.)]|[-*•])\s*', "", l).strip().strip('"“”') for l in text.splitlines()]
    return [l for l in lines if l]


def codex_cmd():
    # Windows 의 npm 전역 'codex' 는 .cmd 껍데기라 Python 이 바로 못 부른다(실측 WinError 2).
    # 여러 줄 한글 지시문이 cmd.exe 를 거치면 깨지므로 node 로 진입 파일을 직접 부른다.
    root = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True, shell=True).stdout.strip()
    js = Path(root) / "@openai" / "codex" / "bin" / "codex.js"
    if not js.exists():
        raise RuntimeError(f"Codex CLI 진입 파일 없음: {js}")
    return ["node", str(js)]


def gen_gpt(model, prompt):
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "out.txt"
        r = subprocess.run([*codex_cmd(), "exec", "--ephemeral", "--skip-git-repo-check", "-s", "read-only", "-C", d,
                            "-m", model, "-o", str(out), prompt + LINES],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900, shell=False)
        if r.returncode or not out.exists():
            raise RuntimeError(f"codex 실패 rc={r.returncode}: {r.stderr[-300:]}")
        return split_lines(out.read_text(encoding="utf-8"))


def gen_gemini(prompt, ks):
    last = None
    for m in GEMINI_CHAIN:
        try:
            return m, exp001.generate(m, prompt, ks)   # exp001.generate 가 한 줄 형식 지시를 붙인다
        except RuntimeError as e:
            last = e
    raise RuntimeError(f"Gemini 3.x Flash 전부 실패: {last}")
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
            if model.startswith("gpt"):
                used, raw = model + " (Codex CLI)", gen_gpt(model, prompt)
            else:
                used, raw = gen_gemini(prompt, ks)
            hooks = [h.strip() for h in raw if str(h).strip()][:N]
            m = {**exp001.measure(hooks), **top_word(hooks)}
            res["runs"].append({"model": model, "model_used": used, "prompt": name, "metrics": m, "hooks": hooks})
            out.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
            print(model, name, m, flush=True)


if __name__ == "__main__":
    main()
