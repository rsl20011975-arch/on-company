"""성과 수집. 발행 후 7일까지 매일, 그 뒤 30일까지 주 1회."""
import datetime as dt, time
from . import ig, store


def run():
    pub = store.load("published.json", {})
    ins = store.load("insights.json", {})
    now = store.now()
    for slug, v in pub.items():
        if not v.get("media_id") or str(v["media_id"]).startswith("dry_"):
            continue
        age = (now - dt.datetime.fromisoformat(v["published_at"])).days
        last = ins.get(slug, {}).get("at")
        if age > 30 or (age > 7 and last and (now - dt.datetime.fromisoformat(last)).days < 7):
            continue
        vals, errs = ig.media_insights(v["media_id"], v.get("kind", "IMAGE"))
        hist = ins.get(slug, {}).get("history", [])
        hist.append({"at": now.isoformat(), "age_days": age, **vals})
        ins[slug] = {"at": now.isoformat(), "kind": v.get("kind"), "latest": vals, "errors": errs, "history": hist[-40:]}
    acct = store.load("account.json", {"days": []})
    try:
        m = ig.me()
        acct["days"].append({"date": now.date().isoformat(), "followers": m.get("followers_count"), "media": m.get("media_count")})
        acct["days"] = list({d["date"]: d for d in acct["days"]}.values())[-400:]
        since = int(time.time()) - 2 * 86400
        for metric, extra in [("reach", {"metric_type": "total_value", "breakdown": "follow_type"}),
                              ("views", {"metric_type": "total_value"}),
                              ("profile_links_taps", {"metric_type": "total_value"})]:
            try:
                acct.setdefault("raw", {})[metric] = ig.account_daily(metric, since, int(time.time()), **extra)
            except ig.IGError as e:
                acct.setdefault("errors", {})[metric] = str(e)[:160]
    except ig.IGError as e:
        acct.setdefault("errors", {})["me"] = str(e)[:160]
    store.save("insights.json", ins); store.save("account.json", acct)
    store.push("insights")
