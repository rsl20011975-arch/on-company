"""실험 008 — AI한테 로또 번호를 뽑아 달라고 하면 정말 무작위일까 (2026-11-01, 온). v4 대중 실험 5호, 실험 006(아무 숫자 → 37) 이어 찍기.

지시문 2종(PROMPTS): 보통 사람이 쓰는 그대로 "로또 번호 6개 뽑아 줘"(20회) · "이번 주 로또 번호 추천해 줘"(10회). 매번 새 대화(Codex --ephemeral).
측정(코드): 답에서 1~45 정수 6개를 읽어 번호별 등장 횟수, 완전히 같은 조합 수를 센다.
진짜 무작위라면 20세트(120개)에서 번호 하나의 평균 등장은 2.7번이고, 한 번호가 10번 이상 나올 확률은 0.1% 미만이다(이항분포).
모델: GPT = Codex CLI gpt-6.1-terra. 실험 006 의 호출 함수를 그대로 쓴다. 호출은 한 번에 하나씩(2026-11-01 실측: Codex 10개 동시 실행은 13분간 한 건도 끝나지 않았다. 단독 호출은 정상).
"""
import importlib.util, json, re, sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("exp006", HERE.parent / "exp006_random_number" / "run.py")
exp006 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(exp006)

PROMPTS = {"pick": ("로또 번호 6개 뽑아 줘.", 20), "recommend": ("이번 주 로또 번호 추천해 줘.", 10)}
RESULTS = HERE / "results.json"


def six(text):
    nums = []
    for m in re.findall(r"\d+", text):
        n = int(m)
        if 1 <= n <= 45 and n not in nums:
            nums.append(n)
        if len(nums) == 6:
            break
    return sorted(nums)


def one(prompt):
    model, text = exp006.ask(prompt)
    return {"model": model, "nums": six(text), "text": text.strip()}


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
                    print(name, len(runs), r["nums"], flush=True)
    for key, runs in res.items():
        c = Counter(x for r in runs for x in r["nums"])
        sets = Counter(tuple(r["nums"]) for r in runs)
        print(key, "번호 TOP", c.most_common(8), "| 같은 조합", [(s, k) for s, k in sets.items() if k > 1])


if __name__ == "__main__":
    main()
