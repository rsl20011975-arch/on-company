"""python -m on_factory <작업>
  daily     : pull → 토큰 → 발행 1건(무작위 지연) → Threads 1건 → 댓글 모으기 → 남은 분량 → 하루 마감 보고(22:40 이후 1회) → 생존 신호
  collect   : 성과 수집
  comments  : 댓글 모으기 + 사장이 쓴 답 게시
  check     : 연결 점검 (계정·한도·토큰·공개 URL) - 발행하지 않는다
"""
import json, sys, traceback, datetime as dt
from . import store, repo_lock, publish, threads_publish, collect, comments, tokens, ig, brief
from .notify import send
from .redact import redact
from .config import QUEUE

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)


def heartbeat(task, ok, note=""):
    h = store.load("health.json", {})
    h[task] = {"at": store.now().isoformat(), "ok": ok, "note": note[:300]}
    store.save("health.json", h)
    store.push(f"heartbeat {task}")


def watchdog():
    """발행 대기분(보류 제외)이 며칠치 남았는지 state/runway.json 에 적는다. 채우는 건 사장 온의 일이라 보통은 적기만 한다.
    하루치도 안 남았을 때만 사람에게 알린다(하루 1회) - 그때는 온의 제작 작업 자체가 멈췄을 가능성이 크고,
    사람이 할 수 있는 일(Claude 앱 켜기)이 있다."""
    dday = store.load("dday.json", {}).get("date")
    if not dday:
        return
    pub = store.load("published.json", {})
    now = store.now()
    queue = json.loads(QUEUE.read_text(encoding="utf-8"))
    pending = [q for q in queue if not pub.get(q["slug"], {}).get("media_id") and not q.get("hold")]
    last = max((publish.due_at(q, dday) for q in pending), default=None)
    rw = store.load("runway.json", {})
    rw.update(checked_at=now.isoformat(), publishable=len(pending), last_due=last.isoformat() if last else None,
              days_left=round((last - now).total_seconds() / 86400, 1) if last else 0)
    if (not last or last < now + dt.timedelta(days=1)) and rw.get("alerted") != now.date().isoformat():
        send(f"ON 발행 대기분이 하루치도 안 남았다(남은 {len(pending)}건). 사장 온의 제작 작업이 멈췄을 수 있다 - "
             "Claude 데스크톱 앱이 켜져 있는지만 확인해 주세요. 내용 판단은 필요 없다.")
        rw["alerted"] = now.date().isoformat()
    store.save("runway.json", rw)


def main(task):
    steps = {"daily": [store.pull, tokens.run, publish.run, threads_publish.run, comments.fetch, watchdog, brief.run],
             "collect": [store.pull, collect.run],
             "comments": [store.pull, comments.fetch, comments.post],
             "check": [store.pull, lambda: print(json.dumps({"me": ig.me(), "limit": ig.publishing_limit()}, ensure_ascii=False))]}[task]
    try:
        with repo_lock.held(task):          # 세 작업이 같은 작업 폴더를 쓴다 - 한 번에 하나만
            _run(task, steps)
    except repo_lock.Busy as e:
        print(e)
        send(f"{task} 건너뜀 - {e}")
        sys.exit(1)


def _run(task, steps):
    try:
        for s in steps:
            s()
        heartbeat(task, True)
    except Exception as e:
        note = redact(f"{type(e).__name__}: {e}")
        traceback.print_exc()
        send(f"{task} 실패 - {note}")
        try:
            heartbeat(task, False, note)
        except Exception:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "check")
