"""bot/threads_queue.json 에서 때가 된 Threads 글 1건을 올린다. publish.py 의 Threads 판.

항목: {"slug", "day", "slot", "parts": [본글, 답글...], "video": 레포 경로 | "images": [레포 경로...]}
  (각 단락 500자 이하, 매체는 본글에 붙는다. 사장실이 쓴다)
멱등: 올리기 전에 의도를 기록한다. 의도만 있고 결과가 없으면 다시 올리지 않고 멈춘다(중복 게시보다 멈춤이 낫다).
"""
import json, datetime as dt
from . import store, threads, announce
from .publish import due_at, interventions, public_url
from .config import ROOT

QUEUE = ROOT / "bot" / "threads_queue.json"
STATE = "threads_published.json"
MIN_GAP_HOURS = 3


def run():
    dday = store.load("dday.json", {}).get("date")
    if not dday or not QUEUE.exists():
        return None
    pub = store.load(STATE, {})
    now = store.now()
    last = max((dt.datetime.fromisoformat(v["at"]) for v in pub.values() if v.get("at")), default=None)
    if last and now - last < dt.timedelta(hours=MIN_GAP_HOURS):
        return None
    queue = json.loads(QUEUE.read_text(encoding="utf-8"))
    due = [q for q in queue if q["slug"] not in pub and due_at(q, dday) <= now]
    stuck = [s for s, v in pub.items() if v.get("intent") and not v.get("ids")]
    if stuck:
        raise RuntimeError(f"Threads {stuck}: 의도만 기록되고 결과 없음 - 프로필에서 실제 게시 여부 확인 후 상태를 고칠 것")
    if not due:
        return None
    item = sorted(due, key=lambda q: due_at(q, dday))[0]
    parts = [p.format(interventions=interventions()) for p in item["parts"]]
    for p in parts:
        if len(p) > threads.MAX_TEXT:
            raise ValueError(f"{item['slug']}: 단락 {len(p)}자 (상한 {threads.MAX_TEXT})")

    video = public_url(item["video"]) if item.get("video") else None
    images = [public_url(f) for f in item.get("images", [])] or None

    threads.me()   # 연결 확인을 의도 기록 앞에 둔다 - 08:57 사고처럼 첫 요청에서 끊겨도 막힘이 남지 않게
    pub[item["slug"]] = {"intent": now.isoformat()}
    store.save(STATE, pub); store.push(f"threads intent {item['slug']}")
    ids = threads.post_thread(parts, video_url=video, image_urls=images)
    pub[item["slug"]] = {"ids": ids, "at": store.now().isoformat(), "source": item.get("source", "")}
    store.save(STATE, pub); store.push(f"threads published {item['slug']}")
    announce.published("Threads", item["slug"], ids[0], "영상" if video else "카드" if images else "글")
    return ids
