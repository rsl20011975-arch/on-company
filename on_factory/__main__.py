"""python -m on_factory <작업>
  daily     : pull → 토큰 → 발행 1건(무작위 지연) → Threads 1건 → 댓글 모으기 → 생존 신호
  collect   : 성과 수집
  comments  : 댓글 모으기 + 사장이 쓴 답 게시
  check     : 연결 점검 (계정·한도·토큰·공개 URL) - 발행하지 않는다
"""
import json, sys, traceback, datetime as dt
from . import store, publish, threads_publish, collect, comments, tokens, ig
from .notify import send
from .config import QUEUE

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)


def heartbeat(task, ok, note=""):
    h = store.load("health.json", {})
    h[task] = {"at": store.now().isoformat(), "ok": ok, "note": note[:300]}
    store.save("health.json", h)
    store.push(f"heartbeat {task}")


def watchdog():
    """사장실(클라우드)이 멈췄는지 본다: 앞으로 낼 것이 3일치 미만이면 알린다."""
    dday = store.load("dday.json", {}).get("date")
    if not dday:
        return
    pub = store.load("published.json", {})
    horizon = store.now() + dt.timedelta(days=3)
    queue = json.loads(QUEUE.read_text(encoding="utf-8"))
    pending = [q for q in queue if not pub.get(q["slug"], {}).get("media_id")]
    if not any(publish.due_at(q, dday) >= horizon for q in pending):
        send(f"남은 게시물 {len(pending)}건, 3일 뒤 분량이 없다 - 사장실(클라우드 온)의 제작이 멈췄을 수 있다")


def main(task):
    steps = {"daily": [store.pull, tokens.run, publish.run, threads_publish.run, comments.fetch, watchdog],
             "collect": [store.pull, collect.run],
             "comments": [store.pull, comments.fetch, comments.post],
             "check": [store.pull, lambda: print(json.dumps({"me": ig.me(), "limit": ig.publishing_limit()}, ensure_ascii=False))]}[task]
    try:
        for s in steps:
            s()
        heartbeat(task, True)
    except Exception as e:
        note = f"{type(e).__name__}: {e}"
        traceback.print_exc()
        send(f"{task} 실패 - {note}")
        try:
            heartbeat(task, False, note)
        except Exception:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "check")
