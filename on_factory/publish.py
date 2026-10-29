"""큐에서 오늘 낼 것 1건을 발행한다. 멱등: 의도를 먼저 기록하고, 결과가 불명이면 실제 피드와 대조한다."""
import json, random, re, time, datetime as dt
import requests
from . import ig, store, audio, announce
import hashlib
from urllib.parse import quote
from .config import ROOT, QUEUE, GH_REPO, DAILY_PUBLISH_MAX, MIN_GAP_HOURS, SLOT_JITTER_MIN


def interventions():
    p = ROOT / "intervention_log.md"
    return sum(1 for l in p.read_text(encoding="utf-8").splitlines() if re.match(r"^\|\s*\d+\s*\|", l)) if p.exists() else 0


def render_caption(item):
    d0 = store.load("dday.json", {}).get("date")  # 사장실이 출시 관문 통과 시 기록
    day = (store.now().date() - dt.date.fromisoformat(d0)).days if d0 else 0
    cap = item["caption"].format(interventions=interventions(), day=day)
    tags = re.findall(r"#\S+", cap)
    if len(tags) > 5:
        raise ValueError(f"{item['slug']}: 해시태그 {len(tags)}개 (상한 5)")
    if len(cap) > 2200:
        raise ValueError(f"{item['slug']}: 캡션 {len(cap)}자 (상한 2200)")
    return cap


def urls(rel):
    """같은 파일의 공개 주소 후보: jsDelivr(커밋 고정) → GitHub raw(커밋 고정)."""
    sha = store.git("rev-parse", "HEAD")
    path = quote(rel)
    return [f"https://cdn.jsdelivr.net/gh/{GH_REPO}@{sha}/{path}",
            f"https://raw.githubusercontent.com/{GH_REPO}/{sha}/{path}"]


def public_url(rel):
    """열리는 첫 주소를 고른다. 영상은 Content-Type 이 video/* 인 주소만 받는다."""
    last = None
    for u in urls(rel):
        try:
            wait_public(u, limit=180, video=rel.endswith(".mp4"))
            return u
        except RuntimeError as e:
            last = e
    raise last


def wait_public(u, limit=300, video=False):
    if ig.DRY:
        return
    t0 = time.time()
    while time.time() - t0 < limit:
        try:
            r = requests.head(u, timeout=15, allow_redirects=True)
            if r.status_code == 200 and (not video or r.headers.get("content-type", "").startswith("video/")):
                return
        except requests.RequestException:
            pass
        time.sleep(10)
    raise RuntimeError(f"공개 URL 이 열리지 않는다: {u}")


def _match_existing(caption):
    head = caption[:60]
    for m in ig.recent_media(30):
        if (m.get("caption") or "")[:60] == head:
            return m["id"]
    return None


def due_at(item, dday):
    """출시일(D+0) + day 일, 슬롯 시각 + 항목별 고정 무작위(±SLOT_JITTER_MIN분)."""
    h, m = map(int, item.get("slot", "18:30").split(":"))
    off = int(hashlib.sha1(item["slug"].encode()).hexdigest(), 16) % (2 * SLOT_JITTER_MIN + 1) - SLOT_JITTER_MIN
    base = dt.datetime.combine(dt.date.fromisoformat(dday) + dt.timedelta(days=item["day"]), dt.time(h, m), tzinfo=store.KST)
    return base + dt.timedelta(minutes=off)


def run():
    dday = store.load("dday.json", {}).get("date")
    if not dday:
        print("출시 전 (state/dday.json 없음) - 발행하지 않는다"); return None
    pub = store.load("published.json", {})
    now = store.now()
    today = now.date().isoformat()
    done_today = [v for v in pub.values() if v.get("date") == today and v.get("media_id")]
    if len(done_today) >= DAILY_PUBLISH_MAX:
        print("오늘 몫은 다 냈다"); return None
    last = max((dt.datetime.fromisoformat(v["published_at"]) for v in pub.values() if v.get("published_at")), default=None)
    if last and now - last < dt.timedelta(hours=MIN_GAP_HOURS):
        print(f"직전 발행 후 {MIN_GAP_HOURS}시간이 안 지났다"); return None
    queue = json.loads(QUEUE.read_text(encoding="utf-8"))
    due = [q for q in queue if not pub.get(q["slug"], {}).get("media_id") and not q.get("hold") and due_at(q, dday) <= now]  # hold = 사장이 세워 둔 것
    if not due:
        print("지금 낼 것이 없다"); return None
    item = sorted(due, key=lambda q: due_at(q, dday))[0]
    if due_at(item, dday).date() < now.date():
        print(f"밀린 항목 {item['slug']} - 오늘 1건으로 낸다 (사장실이 재편성할 것)")
    if not item.get("qa_pass"):
        raise RuntimeError(f"{item['slug']}: 품질 게이트 통과 기록(qa_pass) 없음 - 발행 금지")
    caption = render_caption(item)

    prev = pub.get(item["slug"], {})
    if prev.get("intent"):                       # 지난번에 의도만 남기고 끊겼다 → 피드와 대조
        found = _match_existing(caption)
        if found:
            pub[item["slug"]] = {**prev, "media_id": found, "date": today, "recovered": True}
            store.save("published.json", pub); store.push(f"recovered {item['slug']}")
            announce.published("인스타", item["slug"], found, "끊긴 발행을 피드에서 찾아 복구")
            return found

    files = item["files"]
    if item["type"] == "reel":
        final = audio.build(item)
        rel = final.relative_to(ROOT).as_posix()
        store.push(f"audio {item['slug']}", paths=(rel,))
        files = [rel]
    pub_urls = [public_url(f) for f in files]

    pub[item["slug"]] = {"intent": store.now().isoformat(), "date": today}
    store.save("published.json", pub); store.push(f"intent {item['slug']}")

    t = item["type"]
    if t == "carousel":
        mid = ig.post_carousel(pub_urls, caption)
    elif t == "image":
        mid = ig.post_image(pub_urls[0], caption)
    elif t == "reel":
        mid = ig.post_reel(pub_urls[0], caption, trial=item.get("trial", False))
    elif t == "story":
        mid = ig.post_story(image_url=pub_urls[0])
    else:
        raise ValueError(f"알 수 없는 타입 {t}")

    pub[item["slug"]].update(media_id=mid, kind={"carousel": "CAROUSEL_ALBUM", "reel": "REELS"}.get(t, "IMAGE"),
                             published_at=store.now().isoformat())
    store.save("published.json", pub)
    store.push(f"published {item['slug']} {mid}")
    announce.published("인스타", item["slug"], mid, {"carousel": "카드", "reel": "릴스"}.get(t, t))
    return mid
