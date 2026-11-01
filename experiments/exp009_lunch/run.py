"""실험 009 — AI한테 점심 메뉴를 골라 달라고 하면 매번 다른 걸 고를까 (2026-11-01, 온). v4 대중 실험 6호, 실험 006(아무 숫자 → 37) 이어 찍기 2.

지시문 2종(PROMPTS): "오늘 점심 뭐 먹을지 하나만 골라 줘"(20회) · "점심 메뉴 아무거나 하나 정해 줘. 김치찌개 말고"(10회). 매번 새 대화(Codex --ephemeral).
측정(코드): 답의 첫 줄에서 메뉴 이름을 뽑지 않고 원문을 남긴다 → 메뉴 판독은 온이 judgments.json 에 손으로 적는다(표기 흔들림: 김치찌개/김치 찌개).
모델: GPT = Codex CLI gpt-6.1-terra. 실험 006 의 호출 함수를 그대로 쓴다. 호출은 한 번에 하나씩(2026-11-01 실측: Codex 10개 동시 실행은 13분간 한 건도 끝나지 않았다. 단독 호출은 정상).
"""
import importlib.util, json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("exp006", HERE.parent / "exp006_random_number" / "run.py")
exp006 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(exp006)

PROMPTS = {"pick": ("오늘 점심 뭐 먹을지 하나만 골라 줘.", 20), "notkimchi": ("점심 메뉴 아무거나 하나 정해 줘. 김치찌개 말고.", 10)}
RESULTS = HERE / "results.json"


def one(prompt):
    model, text = exp006.ask(prompt)
    return {"model": model, "text": text.strip()}


def main():
    res = json.loads(RESULTS.read_text(encoding="utf-8")) if RESULTS.exists() else {}
    for name, (prompt, n) in PROMPTS.items():
        runs = res.setdefault(f"gpt_{name}", [])
        need = n - len(runs)
        if need > 0:
            with ThreadPoolExecutor(1) as ex:
                for r in ex.map(one, [prompt] * need):
                    runs.append(r)
                    RESULTS.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
                    print(name, len(runs), r["text"][:40].replace("\n", " "), flush=True)


if __name__ == "__main__":
    main()
