"""실험 012 — AI한테 주말 영화를 추천해 달라고 하면 매번 다를까 (2026-11-01, 온). v4 대중 실험 9호, 실험 009(점심 → 메뉴 2개) 이어 찍기.

지시문(PROMPTS): "주말에 볼 영화 하나만 추천해 줘."(20회). 결과를 본 뒤 1위를 빼 달라는 지시문(10회)을 추가한다(실험 009 와 같은 순서).
측정: 원문을 남기고 영화 제목은 온이 judgments.json 에 손으로 적는다. 매번 새 대화(Codex --ephemeral).
모델: GPT = Codex CLI gpt-6.1-terra. 호출 함수·순차 실행은 실험 011 과 같다.
"""
import importlib.util, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOP = sys.argv[1] if len(sys.argv) > 1 else None   # 먼저 잡는다: 아래 import 사슬(exp002)이 sys.argv 를 지운다
_spec = importlib.util.spec_from_file_location("exp011", HERE.parent / "exp011_rps" / "run.py")
exp011 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(exp011)

PROMPTS = {"pick": ("주말에 볼 영화 하나만 추천해 줘.", 20)}
if TOP:   # python run.py <1위 제목> → 그 영화를 빼 달라는 10회
    PROMPTS["not_top"] = (f"주말에 볼 영화 하나만 추천해 줘. {TOP} 말고.", 10)

if __name__ == "__main__":
    exp011.run(PROMPTS, HERE / "results.json")
