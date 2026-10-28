"""실험 001 — AI에게 릴스 훅을 '그냥' 시키면 vs '사장처럼' 시키면.

같은 주제, 같은 모델, 지시문만 다르게 50개씩 뽑아 코드로 센다(사람 눈대중 없음).
사용: python run.py            -> results.json, summary.md
키: 쇼츠공장 .env 의 GEMINI_API_KEY* 를 프로세스 안에서만 읽는다(출력·저장하지 않음).
"""
import json, re, sys, time, urllib.request, urllib.error
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHORTS_ENV = Path(r"D:\쇼츠\.env")
# 실측 목록(2026-10-28 models API)에서 고름. 3.x Flash(하루 20회)는 쇼츠공장이 쓰는 몫이라 실험에 쓰지 않는다
# (그날 이미 소진, 429). 실험은 한도가 넉넉한 모델로만: Flash-Lite 500/일, Gemma 4 14,400/일.
MODELS = sys.argv[1:] or ["gemini-3.1-flash-lite", "gemma-4-31b-it"]
N = 50
TOPIC = "AI 혼자 운영하는 인스타그램 계정이 팔로워 0명에서 시작하는 실험"

PROMPTS = {
    "plain": f"'{TOPIC}'을 주제로 인스타 릴스 첫 문장(훅)을 {N}개 써줘.",
    "ceo": f"""역할: 한국어 숏폼에서 조회수 상위 1%만 분석해 온 편집장.
상황: {TOPIC}. 시청자는 인스타를 키우고 싶은 1인 사업자·크리에이터.
요청: 릴스 첫 0.5초에 화면에 뜰 훅 {N}개.
규칙:
- 각 훅 22자 이내, 한 문장.
- 절반 이상에 구체적 숫자(날짜·개수·%·원).
- 결과를 먼저 말한다. 설명·인사로 시작하지 않는다.
- 금지: 느낌표, 이모지, '꿀팁', '~하는 법', '놓치면', '대박', '충격', '혁신', '이것만', '비밀'.
- {N}개는 서로 다른 구조로(질문형·숫자형·반전형·손해형·고백형을 섞는다).""",
}
# 001b: 'ceo' 결과를 읽어 보니 팔로워 0명 계정인데 "3일 만에 1,000명 찍었다" 같은 거짓 성과가 나왔다.
# 같은 지시문에 사실 제약만 더해, 구체성은 지키면서 거짓이 사라지는지 잰다.
PROMPTS["ceo_fact"] = PROMPTS["ceo"] + """
사실 제약(가장 중요):
- 이 계정은 오늘 시작했다. 팔로워 0명, 조회수 0, 매출 0원. 아직 아무 성과도 없다.
- 일어나지 않은 성과를 과거형으로 쓰지 않는다("달성했다", "찍었다", "벌었다" 금지).
- 숫자는 지금 사실(0명, D-0, 30일, 목표 1만)·실험 조건(50개, 하루 3편)·질문으로만 쓴다."""

CLICHES = ["꿀팁", "하는 법", "하는법", "놓치면", "대박", "충격", "혁신", "이것만", "비밀", "꼭 알아야", "알아보", "소개합니다", "여러분", "인생", "게임체인저"]
EMOJI = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF]")
# \uAC70\uC9D3 \uC131\uACFC \uC8FC\uC7A5: \uC22B\uC790 + \uC774\uBBF8 \uC774\uB8EC \uACB0\uACFC\uB97C \uB9D0\uD558\uB294 \uC5B4\uBBF8. 0\uBA85 \uACC4\uC815\uC5D0\uC11C \uC774 \uD615\uD0DC\uB294 \uC804\uBD80 \uC0AC\uC2E4\uC774 \uC544\uB2C8\uB2E4.
CLAIM = re.compile(r"\d[\d,.]*\s*(\uBA85|\uB9CC|\uCC9C|\uC6D0|%|\uBC30|\uD68C|\uBDF0).*?(\uB2EC\uC131|\uCC0D\uC5C8|\uCC0D\uC740|\uB118\uACBC|\uB0C8\uB2E4|\uB0B8 |\uBC8C\uC5C8|\uBC88 |\uBC8C\uAE30 \uC2DC\uC791|\uB298\uC5C8|\uB298\uB838|\uC62C\uB838|\uAE30\uB85D|\uC99D\uAC00|\uC0C1\uC2B9|\uC131\uC7A5\uC2DC\uD0A8|\uBAA8\uC740|\uBAA8\uC558|\uC0B4\uB824\uB0C8|\uC904\uC600|\uBC14\uB010|\uB6F4)")


def keys():
    out = []
    for line in SHORTS_ENV.read_text(encoding="utf-8").splitlines():
        if re.match(r"\s*GEMINI_API_KEY(_\d+)?\s*=", line):
            out.append(line.split("=", 1)[1].strip())
    return [k for k in out if k]


def generate(model, prompt, ks):
    # JSON 스키마 강제는 Flash-Lite 에서 503 이 났다(2026-10-28 실측, 평문은 성공). 한 줄에 하나로 받아 코드가 자른다.
    prompt += "\n\n출력 형식: 훅만 한 줄에 하나씩. 번호·따옴표·설명 없이."
    body = json.dumps({
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 1.0},
    }).encode()
    last = None
    for k in ks * 2:                          # 503(과부하)은 한 바퀴 돈 뒤 한 번 더
        if last == "503":
            time.sleep(15)
        req = urllib.request.Request(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={k}",
            data=body, headers={"Content-Type": "application/json"})
        try:
            j = json.load(urllib.request.urlopen(req, timeout=180))
            text = "".join(p.get("text", "") for p in j["candidates"][0]["content"]["parts"] if not p.get("thought"))
            lines = [re.sub(r'^\s*(\d+[.)]|[-*•])\s*', "", l).strip().strip('"“”') for l in text.splitlines()]
            return [l for l in lines if l]
        except urllib.error.HTTPError as e:
            last = f"{e.code}"
            if e.code in (429, 500, 503):
                last = "503" if e.code != 429 else last
                continue                      # 429=다음 키(프로젝트별 한도), 500/503=구글 쪽 일시 오류(통제 밖)
        except TimeoutError:
            last = "503"
            continue
            raise RuntimeError(f"{model} HTTP {e.code}: {e.read()[:300]!r}")
    raise RuntimeError(f"{model}: 모든 키 실패 (마지막 {last})")


def bigrams(s):
    s = re.sub(r"\s+", "", s)
    return {s[i:i + 2] for i in range(len(s) - 1)}


def measure(hooks):
    n = len(hooks)
    cl = [h for h in hooks if any(c in h for c in CLICHES)]
    ex = [h for h in hooks if "!" in h]
    em = [h for h in hooks if EMOJI.search(h)]
    num = [h for h in hooks if re.search(r"\d", h)]
    # 거의 같은 문장: 글자 2-gram 자카드 0.6 이상인 쌍이 하나라도 있으면 중복으로 센다
    bg = [bigrams(h) for h in hooks]
    dup = set()
    for i in range(n):
        for j in range(i + 1, n):
            u = bg[i] | bg[j]
            if u and len(bg[i] & bg[j]) / len(u) >= 0.6:
                dup.update((i, j))
    # 첫 두 글자(시작 패턴) 다양성
    starts = {re.sub(r"\s+", "", h)[:2] for h in hooks}
    lens = sorted(len(h) for h in hooks)
    pct = lambda x: round(100 * len(x) / n, 1) if n else 0
    ai = [h for h in hooks if "AI" in h.upper()]
    claim = [h for h in hooks if CLAIM.search(h)]
    return {"n": n, "fake_claim_pct": pct(claim), "has_AI_pct": pct(ai), "cliche_pct": pct(cl), "exclaim_pct": pct(ex), "emoji_pct": pct(em),
            "number_pct": pct(num), "near_dup_pct": round(100 * len(dup) / n, 1) if n else 0,
            "distinct_starts": len(starts), "median_len": lens[n // 2] if n else 0,
            "over22_pct": pct([h for h in hooks if len(h) > 22])}


def main():
    ks = keys()
    if not ks:
        sys.exit("쇼츠공장 .env 에 GEMINI_API_KEY 가 없다")
    out = HERE / "results.json"
    results = json.loads(out.read_text(encoding="utf-8")) if out.exists() else \
        {"topic": TOPIC, "n": N, "at": time.strftime("%Y-%m-%d %H:%M"), "prompts": PROMPTS, "runs": []}
    done = {(r["model"], r["prompt"]) for r in results["runs"]}
    for model in MODELS:
        for name, prompt in PROMPTS.items():
            if (model, name) in done:
                continue                      # 이미 잰 칸은 다시 뽑지 않는다(같은 실험을 이어서 채움)
            hooks = [h.strip() for h in generate(model, prompt, ks) if str(h).strip()][:N]
            m = measure(hooks)
            results["runs"].append({"model": model, "prompt": name, "metrics": m, "hooks": hooks})
            out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
            print(model, name, m, flush=True)


if __name__ == "__main__":
    main()
