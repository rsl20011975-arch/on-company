"""하루 마감 보고. 22:40 이후 첫 daily 실행에서 텔레그램으로 하루 1회 보낸다(state/brief.json 이 보낸 날짜를 기억한다).

2026-10-29 개입 21·22번: 보고서는 파일에만 쓰고 텔레그램은 '사람 손이 필요할 때만' 쓰게 설계해서,
주주에게는 발행·성과 보고가 하나도 가지 않았다. 실패 알림은 따로 즉시 가고, 이것은 정상인 날의 보고다.
공장이 보내므로 Claude 앱이 꺼져 있어도 온다.
"""
import json, datetime as dt
from . import store, publish, ig, threads
from .config import QUEUE, ROOT
from .notify import send

SEND_AFTER = dt.time(22, 40)          # 마지막 편성(인스타 21:30, Threads 22:05 ±20분) 뒤
THREADS_QUEUE = ROOT / "bot" / "threads_queue.json"


def _ig_numbers(v):
    vals, errs = ig.media_insights(v["media_id"], v.get("kind", "IMAGE"))
    s = f"조회 {vals.get('views', '?')} · 도달 {vals.get('reach', '?')} · 저장 {vals.get('saved', '?')} · 공유 {vals.get('shares', '?')}"
    if vals.get("ig_reels_avg_watch_time"):
        s += f" · 평균 시청 {vals['ig_reels_avg_watch_time'] / 1000:.1f}초"
    return s + (f" (오류 {list(errs)})" if errs else "")


def _th_numbers(mid):
    m = {i["name"]: i["values"][0]["value"] for i in threads.insights(mid)}
    return f"조회 {m.get('views', '?')} · 좋아요 {m.get('likes', '?')} · 답글 {m.get('replies', '?')}"


def _live(fn, *a):
    try:
        return fn(*a)
    except Exception as e:                 # 숫자 하나 못 읽었다고 보고 전체를 막지 않는다 - 보고 안에 그대로 보인다
        return f"못 읽음({type(e).__name__}: {str(e)[:60]})"


def _upcoming(path, done, dday, day):
    q = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    return sorted((publish.due_at(i, dday).strftime("%H:%M"), i["slug"]) for i in q
                  if i["slug"] not in done and not i.get("hold") and publish.due_at(i, dday).date() == day)


def compose(now):
    dday = store.load("dday.json", {})["date"]
    today, tomorrow = now.date(), now.date() + dt.timedelta(days=1)
    pub = {k: v for k, v in store.load("published.json", {}).items() if v.get("media_id")}
    tpub = store.load("threads_published.json", {})
    week = now - dt.timedelta(days=7)
    me = _live(ig.me)
    out = [f"사장 온 하루 보고 D+{(today - dt.date.fromisoformat(dday)).days} ({today})",
           f"팔로워 {me.get('followers_count') if isinstance(me, dict) else me} · 사람 개입 누적 {publish.interventions()}회", "",
           "[인스타 - 최근 7일 게시물]"]
    for slug, v in pub.items():
        if dt.datetime.fromisoformat(v["published_at"]) >= week:
            out.append(f"- {slug} ({v['published_at'][5:16].replace('T', ' ')}): {_live(_ig_numbers, v)}")
    out.append("[Threads - 최근 7일 글]")
    for slug, v in tpub.items():
        mid = (v.get("ids") or [v.get("id")])[0]
        if mid and v.get("at") and dt.datetime.fromisoformat(v["at"]) >= week:
            out.append(f"- {slug} ({v['at'][5:16].replace('T', ' ')}): {_live(_th_numbers, mid)}")
    up = _upcoming(QUEUE, pub, dday, tomorrow) + _upcoming(THREADS_QUEUE, tpub, dday, tomorrow)
    out += ["", f"[내일 편성 {len(up)}건]"] + [f"- {t} {s}" for t, s in sorted(up)]
    rw = store.load("runway.json", {})
    bad = [f"{k}: {v['note'][:80]}" for k, v in store.load("health.json", {}).items() if not v.get("ok")]
    out += ["", f"남은 발행분 {rw.get('days_left', '?')}일치 ({rw.get('publishable', '?')}건)",
            "공장 고장: " + ("; ".join(bad) if bad else "없음"),
            "사람 필요: " + ("Claude 앱 켜기(남은 분량 하루 미만)" if (rw.get("days_left") or 0) < 1 else "없음")]
    return "\n".join(out)


def run(force=False):
    now = store.now()
    if not store.load("dday.json", {}).get("date"):
        return
    if not force and (now.time() < SEND_AFTER or store.load("brief.json", {}).get("sent") == now.date().isoformat()):
        return
    if not send(compose(now)):
        raise RuntimeError("하루 보고 텔레그램 전송 실패")
    if not force:                          # 손으로 보낸 것(--now)은 그날 밤 자동 보고를 막지 않는다
        store.save("brief.json", {"sent": now.date().isoformat(), "at": now.isoformat()})


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    run(force="--now" in sys.argv)
