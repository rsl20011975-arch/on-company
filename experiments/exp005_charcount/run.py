"""실험 005 — AI한테 자소서 글자 수를 맞춰 달라고 하면 맞출까 (2026-10-30, 온). 30일 작전 v4 의 두 번째 '대중 실험'.

과제: 자기소개서 '지원 동기' 항목(가상의 지원자·회사, 아래 SPEC). 취준생이 실제로 쓰는 조건 그대로 "공백 포함 500자 이내".
지시문 2종 × 5회:
  plain  = 보통 사람이 쓰는 그대로: "공백 포함 500자 이내로 써 줘"
  check  = 흔히 도는 요령: 450~500자 + "다 쓰고 글자 수를 세어 보고 안 맞으면 고쳐서 최종본만"
측정(코드): 본문의 줄바꿈을 지우고 len() = 공백 포함 글자 수. 500자 초과 = 그대로 내면 접수가 막힌다. 450~500 = 칸을 90% 이상 채움.
모델: GPT = Codex CLI gpt-6.1-terra. 채팅처럼 쓰려고 "도구·명령 쓰지 말고 텍스트로만"을 붙인다(코드로 세지 못하게).
Gemini 3.x Flash 는 2026-10-30 새벽 12개 키 모두 일일 한도(태평양 자정 = 한국 16시 초기화) → `python run.py gemini` 로 나중에 채운다.
사용: python run.py [gpt|gemini]
"""
import importlib.util, json, sys, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
WHO = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in ("gpt", "gemini") else "gpt"
_spec = importlib.util.spec_from_file_location("exp002", HERE.parent / "exp002_diverse" / "run.py")
exp002 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(exp002)

SPEC = ("지원 회사: 가상의 식품 회사 '한솥푸드', 지원 직무: 신입 마케팅.\n"
        "지원자 경험: 대학 동아리에서 학교 앞 카페 인스타그램 계정을 6개월 운영해 팔로워를 300명에서 2,100명으로 늘림. "
        "편의점 아르바이트 1년 동안 신제품 진열 위치를 바꿔 보는 일을 맡음.")
PROMPTS = {
    "plain": "자기소개서 '지원 동기' 항목을 써 줘. 공백 포함 500자 이내야.\n\n" + SPEC,
    "check": ("자기소개서 '지원 동기' 항목을 써 줘. 공백 포함 450자 이상 500자 이하로 맞춰야 해. "
              "다 쓰고 나서 글자 수를 직접 세어 보고, 범위를 벗어나면 고쳐서 최종본만 줘.\n\n" + SPEC),
}
TAIL = "\n\n출력 형식: 자기소개서 본문만. 제목·글자 수 표기·설명 없이. 도구나 명령은 쓰지 말고 텍스트로만 답한다."
RUNS = 5
RESULTS = HERE / "results.json"


def gpt(prompt):
    import subprocess, tempfile
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "out.txt"
        r = subprocess.run([*exp002.codex_cmd(), "exec", "--ephemeral", "--skip-git-repo-check", "-s", "read-only", "-C", d,
                            "-m", "gpt-6.1-terra", "-o", str(out), prompt + TAIL],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)
        if r.returncode or not out.exists():
            raise RuntimeError(f"codex 실패 rc={r.returncode}: {r.stderr[-300:]}")
        return "gpt-6.1-terra", out.read_text(encoding="utf-8")


def gemini(prompt):
    body = json.dumps({"contents": [{"role": "user", "parts": [{"text": prompt + TAIL}]}]}).encode()
    last = None
    for m in exp002.GEMINI_CHAIN:
        for k in exp002.exp001.keys():
            req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={k}",
                                         data=body, headers={"Content-Type": "application/json"})
            try:
                j = json.load(urllib.request.urlopen(req, timeout=180))
                return m, "".join(p.get("text", "") for p in j["candidates"][0]["content"]["parts"] if not p.get("thought"))
            except Exception as e:      # 429·5xx → 다음 키. 키 문자열은 오류에 싣지 않는다
                last = f"{m}: {type(e).__name__}"
    raise RuntimeError(f"Gemini 전부 실패: {last}")


def count(text):
    body = "".join(l.strip() for l in text.strip().splitlines() if l.strip())   # 줄바꿈 제거(입력 칸에 붙여 넣는 모양)
    return len(body), len(body.replace(" ", ""))


def main():
    res = json.loads(RESULTS.read_text(encoding="utf-8")) if RESULTS.exists() else {}
    for name, prompt in PROMPTS.items():
        key = f"{WHO}_{name}"
        runs = res.setdefault(key, [])
        while len(runs) < RUNS:
            model, text = (gpt if WHO == "gpt" else gemini)(prompt)
            n, n_ns = count(text)
            runs.append({"model": model, "chars": n, "chars_no_space": n_ns, "text": text.strip()})
            RESULTS.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
            print(key, len(runs), model, n, flush=True)
    for key, runs in res.items():
        c = [r["chars"] for r in runs]
        print(key, c, "초과", sum(x > 500 for x in c), "450~500", sum(450 <= x <= 500 for x in c))


if __name__ == "__main__":
    main()
