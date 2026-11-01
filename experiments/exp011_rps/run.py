"""실험 011 — AI랑 가위바위보를 하면 매번 다른 걸 낼까 (2026-11-01, 온). v4 대중 실험 8호, 실험 006·008·009('아무거나' → 같은 답) 이어 찍기 4.

지시문 2종(PROMPTS): "가위바위보 하자. 너 먼저 하나 내 줘."(20회) · "가위바위보 하자. 진짜 무작위로 하나만 내 줘."(10회). 매번 새 대화(Codex --ephemeral).
측정: 원문을 남기고 낸 손은 온이 judgments.json 에 손으로 적는다. 진짜 무작위라면 20번 중 한 손이 15번 이상 나올 확률은 0.5% 미만(이항분포 p=1/3).
모델: GPT = Codex CLI gpt-6.1-terra. 실험 006 의 호출 함수를 그대로 쓴다. 호출은 한 번에 하나씩(2026-11-01 실측: 동시 실행은 멈춘다).
"""
import importlib.util, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("exp006", HERE.parent / "exp006_random_number" / "run.py")
exp006 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(exp006)

PROMPTS = {"play": ("가위바위보 하자. 너 먼저 하나 내 줘.", 20), "random": ("가위바위보 하자. 진짜 무작위로 하나만 내 줘.", 10)}
RESULTS = HERE / "results.json"


def run(prompts, results):
    res = json.loads(results.read_text(encoding="utf-8")) if results.exists() else {}
    for name, (prompt, n) in prompts.items():
        runs = res.setdefault(f"gpt_{name}", [])
        while len(runs) < n:
            model, text = exp006.ask(prompt)
            runs.append({"model": model, "text": text.strip()})
            results.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
            print(name, len(runs), text.strip()[:40].replace("\n", " "), flush=True)


if __name__ == "__main__":
    run(PROMPTS, RESULTS)
