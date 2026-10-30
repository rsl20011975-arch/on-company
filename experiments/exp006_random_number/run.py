"""실험 006 — AI한테 1~100 중 아무 숫자나 골라 달라고 하면 정말 아무 숫자일까 (2026-10-30, 온). v4 대중 실험 3호.

지시문 3종(PROMPTS): 보통 사람이 쓰는 그대로 1~100(20회) · 1~10(10회) · "진짜 무작위로, 흔한 숫자는 피해서"(10회). 매번 새 대화(Codex --ephemeral).
측정(코드): 답에서 첫 정수를 읽어 빈도를 센다. 진짜 무작위(균등)라면 20번 중 같은 숫자가 나올 확률은 약 87%지만
한 숫자가 5번 이상 나올 확률은 0.1% 미만 → 같은 숫자가 몇 번 겹치는지가 지표다.
모델: GPT = Codex CLI gpt-6.1-terra. Gemini 는 한국 16시 한도 초기화 후 `python run.py gemini`.
"""
import importlib.util, json, re, sys, urllib.request
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
WHO = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in ("gpt", "gemini") else "gpt"
_spec = importlib.util.spec_from_file_location("exp002", HERE.parent / "exp002_diverse" / "run.py")
exp002 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(exp002)
_spec5 = importlib.util.spec_from_file_location("exp005", HERE.parent / "exp005_charcount" / "run.py")

PROMPTS = {   # 이름: (지시문, 회수)
    "pick100": ("1부터 100 중에 아무 숫자나 하나 골라 줘.", 20),
    "pick10": ("1부터 10 중에 아무 숫자나 하나 골라 줘.", 10),
    "avoid100": ("1부터 100 중에 진짜 무작위로 숫자 하나만 골라 줘. 사람들이 자주 고르는 숫자는 피해서.", 10),
}
TAIL = "\n\n도구나 명령은 쓰지 말고 텍스트로만 답한다."
RESULTS = HERE / "results.json"


def ask(prompt):
    sys.argv = [sys.argv[0], WHO]                 # exp005 가 argv 로 모델을 읽는다
    exp005 = importlib.util.module_from_spec(_spec5); _spec5.loader.exec_module(exp005)
    exp005.TAIL = TAIL
    return (exp005.gpt if WHO == "gpt" else exp005.gemini)(prompt)


def first_int(text):
    m = re.search(r"\d+", text)
    return int(m.group()) if m else None


def main():
    res = json.loads(RESULTS.read_text(encoding="utf-8")) if RESULTS.exists() else {}
    for name, (prompt, n) in PROMPTS.items():
        runs = res.setdefault(f"{WHO}_{name}", [])
        while len(runs) < n:
            model, text = ask(prompt)
            runs.append({"model": model, "n": first_int(text), "text": text.strip()})
            RESULTS.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
            print(WHO, name, len(runs), runs[-1]["n"], flush=True)
    for key, runs in res.items():
        print(key, Counter(r["n"] for r in runs).most_common())


if __name__ == "__main__":
    main()
