"""댓글: 공장은 모으고(inbox) 게시만 한다(outbox). 답은 사장 온이 레포에 쓴다.
private reply(키워드 DM)는 실제 작동 확인 전까지 쓰지 않는다(이사회 P0 #5)."""
import random, time
from . import ig, store


def fetch():
    pub = store.load("published.json", {})
    inbox = store.load("comments_inbox.json", {})
    for slug, v in pub.items():
        mid = v.get("media_id")
        if not mid or str(mid).startswith("dry_"):
            continue
        for c in ig.comments(mid):
            if c["id"] in inbox:
                continue
            me_replied = any(r.get("username") == v.get("username") for r in (c.get("replies") or {}).get("data", []))
            inbox[c["id"]] = {"slug": slug, "media_id": mid, "user": c.get("username"), "text": c.get("text"),
                              "at": c.get("timestamp"), "answered": me_replied}
    store.save("comments_inbox.json", inbox)
    store.push("comments inbox")


def post():
    out = store.load("comments_outbox.json", {})
    inbox = store.load("comments_inbox.json", {})
    sent = 0
    for cid, r in out.items():
        if r.get("posted") or r.get("skip"):
            continue
        ig.reply(cid, r["message"])
        r["posted"] = store.now().isoformat()
        if cid in inbox:
            inbox[cid]["answered"] = True
        sent += 1
        time.sleep(random.randint(40, 180))     # 사람 속도. 연달아 쏘지 않는다
    store.save("comments_outbox.json", out); store.save("comments_inbox.json", inbox)
    store.push(f"replies {sent}")
    return sent
