"""일일 실행기. 큐(queue.json)에서 오늘 날짜(KST) 이하의 미발행 항목을 발행하고 log.json에 기록.
사용: python3 run.py publish | collect | status
이미지 URL은 ASSET_BASE + 상대경로 (공개 GitHub raw URL).
"""
import os, sys, json, datetime, pathlib
sys.path.insert(0, os.path.dirname(__file__))
import ig

ROOT = pathlib.Path(__file__).resolve().parent.parent  # /home/user/insta (레포 루트)
QUEUE = ROOT / "bot" / "queue.json"
LOG = ROOT / "bot" / "log.json"
ASSET_BASE = os.environ.get("ASSET_BASE", "")  # 예: https://raw.githubusercontent.com/<owner>/<repo>/main/

def kst_today():
    return (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=9)).date()

def load(p, default):
    return json.loads(p.read_text()) if p.exists() else default

def save(p, obj):
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2))

def url(rel):
    if not ASSET_BASE:
        raise SystemExit("ASSET_BASE 없음 (공개 이미지 호스팅 URL)")
    return ASSET_BASE.rstrip("/") + "/" + rel.lstrip("/")

def publish():
    q = load(QUEUE, []); log = load(LOG, [])
    today = kst_today(); done = 0
    for item in q:
        if item.get("published") or datetime.date.fromisoformat(item["date"]) > today:
            continue
        t = item["type"]
        if t == "carousel":
            mid = ig.post_carousel([url(f) for f in item["files"]], item["caption"])
        elif t == "image":
            mid = ig.post_image(url(item["files"][0]), item["caption"])
        elif t == "reel":
            mid = ig.post_reel(url(item["files"][0]), item["caption"], trial=item.get("trial", False))
        elif t == "story":
            mid = ig.post_story(image_url=url(item["files"][0]))
        else:
            raise SystemExit(f"알 수 없는 타입 {t}")
        item["published"] = True; item["media_id"] = mid
        item["published_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat() + "Z"
        log.append({"date": item["date"], "slug": item["slug"], "type": t, "media_id": mid})
        print(f"발행: {item['slug']} -> {mid}"); done += 1
        save(QUEUE, q); save(LOG, log)
    print(f"완료 {done}건")

def collect():
    log = load(LOG, [])
    for e in log:
        if e["type"] == "story": continue
        try:
            e["insights"] = ig.media_insights(e["media_id"])
            e["collected_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat() + "Z"
        except SystemExit as ex:
            e["insights_error"] = str(ex)
    save(LOG, log)
    acct = ig.account_insights(7)
    save(ROOT / "bot" / "account_insights.json", {"at": datetime.datetime.now(datetime.timezone.utc).isoformat()+"Z", "data": acct, "me": ig.me()})
    print(json.dumps(log[-7:], ensure_ascii=False, indent=2))

def status():
    q = load(QUEUE, [])
    for i in q:
        print(("✅" if i.get("published") else "⏳"), i["date"], i["type"], i["slug"])

if __name__ == "__main__":
    globals()[sys.argv[1] if len(sys.argv) > 1 else "status"]()
