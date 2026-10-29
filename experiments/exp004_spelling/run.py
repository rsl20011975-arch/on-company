"""실험 004 — AI 맞춤법 검사, 믿어도 되나 (2026-10-30, 온). 30일 작전 v4 의 첫 '대중 실험'.

문장 30개 = 흔히 틀리는 맞춤법 1곳씩 넣은 20개 + 맞는 문장 10개(함정: 고칠 필요가 없다). 순서는 고정 셔플.
보통 사람이 쓰는 지시문 그대로 시킨다: "맞춤법 고쳐 줘, 틀린 데 없으면 그대로".
측정(코드): 틀린 문장 → 고침(정답 표기 있음 + 틀린 표기 없음) / 놓침. 맞는 문장 → 그대로 / 괜히 바꿈(공백·끝 문장부호 무시).
정답 표기는 표준국어대사전 기준(온이 정함 - summary 한계에 적는다). 모델마다 3회(분산을 본다 - 002 의 한계 보완).
모델: 시청자가 쓰는 AI. GPT = Codex CLI gpt-6.1-terra, Gemini = 3.x Flash(실제 응답 모델 기록). Claude 는 실험자라 뺀다.
"""
import importlib.util, json, random, re, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
# 세트는 exp002 를 불러오기 전에 읽는다 - exp002 가 불러올 때 sys.argv 를 지운다(2026-10-30 실측: "hard" 가 무시되고 easy 로 돌았다)
SET = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in ("easy", "hard") else "easy"
_spec = importlib.util.spec_from_file_location("exp002", HERE.parent / "exp002_diverse" / "run.py")
exp002 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(exp002)
exp001 = exp002.exp001

# (문장, 틀린 표기, 정답 표기) - 틀린 문장 20
WRONG = [("이거 이렇게 하면 되?", "되?", "돼?"), ("그건 지금 하면 안 되요.", "되요", "돼요"), ("왠일로 이렇게 일찍 왔어?", "왠일", "웬일"),
         ("회의가 금새 끝났다.", "금새", "금세"), ("몇일 뒤에 다시 보자.", "몇일", "며칠"), ("설레임 가득한 첫 출근이었다.", "설레임", "설렘"),
         ("제 바램은 딱 하나예요.", "바램", "바람"), ("각자 역활을 나눠서 하자.", "역활", "역할"), ("오늘 희안한 일이 생겼다.", "희안", "희한"),
         ("내일 다시 연락할께요.", "할께", "할게"), ("정말 오랫만에 만났다.", "오랫만", "오랜만"), ("서류를 일일히 확인했다.", "일일히", "일일이"),
         ("이건 진짜 어의가 없네.", "어의", "어이"), ("준비가 벌써 다 됬다.", "됬다", "됐다"), ("그럼 내일 뵈요.", "뵈요", "봬요"),
         ("감기가 이제 다 낳았다.", "낳았다", "나았다"), ("이제 어떻하지?", "어떻하", "어떡하"), ("그러던지 말던지 마음대로 해.", "그러던지", "그러든지"),
         ("발표는 문안하게 끝났다.", "문안하게", "무난하게"), ("오늘 운동할려고 했는데 비가 왔다.", "할려고", "하려고")]
RIGHT = ["오늘 날씨가 참 좋네요.", "회의는 세 시에 시작합니다.", "며칠 동안 고민했어요.", "그럴 리가 없어요.", "어이없는 실수였다.",
         "이 정도면 무난하다.", "금세 다시 연락할게요.", "웬만하면 오늘 끝내자.", "다 됐으니 이제 가도 돼요.", "선생님을 뵈러 갔다."]
# 2라운드(hard, 2026-10-30): 1라운드(easy)에서 GPT 가 3회 모두 20/20 - 천장이라 모델 차이가 안 보였다. 문맥으로 갈리는 것만 모았다.
HARD_WRONG = [("문제를 맞추면 상품을 드립니다.", "맞추면", "맞히면"), ("가는 길에 편의점에 들렸다.", "들렸다", "들렀다"),
              ("아이에게 한글을 가르켰다.", "가르켰다", "가르쳤다"), ("부장님 결제를 받아야 해요.", "결제를", "결재를"),
              ("그는 학생으로써 최선을 다했다.", "학생으로써", "학생으로서"), ("싸움 대신 대화로서 문제를 풀었다.", "대화로서", "대화로써"),
              ("열심히 일한 만큼 댓가를 받았다.", "댓가", "대가"), ("이 사람은 제 동생이예요.", "동생이예요", "동생이에요"),
              ("있다가 저녁에 전화할게.", "있다가", "이따가"), ("곧 비가 올 것 같애.", "같애", "같아"),
              ("일이 잘되길 바래요.", "바래요", "바라요"), ("이곳에서는 흡연을 삼가해 주세요.", "삼가해", "삼가"),
              ("그건 너무 어줍잖은 변명이다.", "어줍잖은", "어쭙잖은"), ("숙제를 아직 않 했다.", "않 했다", "안 했다"),
              ("내노라하는 전문가들이 모였다.", "내노라하는", "내로라하는"), ("곰곰히 생각해 봤다.", "곰곰히", "곰곰이"),
              ("방을 깨끗히 치웠다.", "깨끗히", "깨끗이"), ("구지 그럴 필요 없어.", "구지", "굳이"),
              ("얼마 전에 뵜던 분이에요.", "뵜던", "뵀던"), ("계산했으면 영수증을 띄어 주세요.", "띄어", "떼어")]
HARD_RIGHT = ["오늘은 왠지 기분이 좋다.", "웬 떡이야?", "이따가 다시 전화할게.", "학생으로서 부끄럽지 않게 살자.", "결재 서류를 올렸다.",
              "그는 우리 형이에요.", "일이 잘되길 바라요.", "답을 정확히 맞혔다.", "가는 길에 서점에 들렀다.", "흡연을 삼가 주시기 바랍니다."]
_W, _R = (HARD_WRONG, HARD_RIGHT) if SET == "hard" else (WRONG, RIGHT)
ITEMS = [{"s": s, "bad": b, "good": g} for s, b, g in _W] + [{"s": s} for s in _R]
random.Random(4).shuffle(ITEMS)
RESULTS = HERE / ("results.json" if SET == "easy" else "results_hard.json")
PROMPT = ("아래 문장들의 맞춤법을 고쳐 줘. 틀린 데가 없는 문장은 그대로 둬.\n"
          "번호를 붙여서 한 줄에 한 문장씩, 고친 문장만 써 줘. 설명은 쓰지 마.\n\n"
          + "\n".join(f"{i+1}. {it['s']}" for i, it in enumerate(ITEMS)))
RUNS = 3


def gemini(prompt, ks):
    import urllib.request
    body = json.dumps({"contents": [{"role": "user", "parts": [{"text": prompt}]}]}).encode()
    last = None
    for m in exp002.GEMINI_CHAIN:
        for k in ks:
            req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={k}",
                                         data=body, headers={"Content-Type": "application/json"})
            try:
                j = json.load(urllib.request.urlopen(req, timeout=180))
                return m, "".join(p.get("text", "") for p in j["candidates"][0]["content"]["parts"] if not p.get("thought"))
            except Exception as e:      # 429·5xx → 다음 키, 키가 다 막히면 다음 모델. 마지막 오류는 아래에서 그대로 올린다
                last = f"{m}: {type(e).__name__} {str(e)[:120]}"
    raise RuntimeError(f"Gemini 전부 실패: {last}")


def gpt(prompt):
    return "gpt-6.1-terra", "\n".join(exp002.gen_gpt("gpt-6.1-terra", prompt.replace(exp002.LINES, "")))


def parse(text):
    """번호 붙은 줄을 번호로 읽는다. GPT 경로(exp002.gen_gpt)는 번호를 지워서 돌려주므로(2026-10-30 실측: 3회 모두 번호 없는 30줄),
    번호가 하나도 없고 줄 수가 문장 수와 같을 때만 순서로 맞춘다. 줄 수가 다르면 못 읽음으로 센다(추측해서 맞추지 않는다)."""
    out = {}
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for l in lines:
        m = re.match(r"^\s*(\d+)[.)]\s*(.+)$", l)
        if m:
            out[int(m.group(1))] = m.group(2).strip()
    if not out and len(lines) == len(ITEMS):
        out = {i: l for i, l in enumerate(lines, 1)}
    return out


def rescore():
    path = RESULTS; res = json.loads(path.read_text(encoding="utf-8"))
    for r in res["runs"]:
        r["score"] = score(parse(r["raw"]))
    path.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    return res


norm = lambda s: re.sub(r"[\s.?!,]", "", s)


def score(out):
    r = {"fixed": 0, "missed": [], "kept": 0, "overfixed": [], "unparsed": 0}
    for i, it in enumerate(ITEMS, 1):
        o = out.get(i)
        if o is None:
            r["unparsed"] += 1; continue
        if "bad" in it:
            if it["good"] in o and it["bad"] not in o: r["fixed"] += 1
            else: r["missed"].append({"in": it["s"], "out": o})
        elif norm(o) == norm(it["s"]): r["kept"] += 1
        else: r["overfixed"].append({"in": it["s"], "out": o})
    return r


def main():
    ks = exp001.keys()
    path = RESULTS
    res = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"at": time.strftime("%Y-%m-%d %H:%M"), "prompt": PROMPT, "items": ITEMS, "runs": []}
    for who in ("gpt", "gemini"):
        for k in range(RUNS):
            if any(r["who"] == who and r["k"] == k for r in res["runs"]): continue
            model, text = gpt(PROMPT) if who == "gpt" else gemini(PROMPT, ks)
            sc = score(parse(text))
            res["runs"].append({"who": who, "k": k, "model": model, "raw": text, "score": sc})
            path.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
            print(who, k, model, "고침", sc["fixed"], "/20 · 괜히 바꿈", len(sc["overfixed"]), "/10 · 못 읽음", sc["unparsed"], flush=True)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
