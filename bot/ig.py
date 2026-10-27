"""Instagram API (Instagram Login, graph.instagram.com) 최소 클라이언트.
환경변수: IG_ACCESS_TOKEN (장기 토큰, 60일), 선택: IG_USER_ID
의존성: requests
"""
import os, time, json, sys, requests

API = "https://graph.instagram.com/v23.0"
TOKEN = os.environ.get("IG_ACCESS_TOKEN")
DRY = os.environ.get("IG_DRY_RUN") == "1"

def _req(method, path, **params):
    if not TOKEN and not DRY:
        raise SystemExit("IG_ACCESS_TOKEN 없음")
    params["access_token"] = TOKEN or "DRY"
    if DRY:
        print(f"[DRY] {method} {path} {json.dumps({k:v for k,v in params.items() if k!='access_token'}, ensure_ascii=False)[:300]}")
        return {"id": "dry_" + str(int(time.time())), "user_id": "dry_uid", "status_code": "FINISHED", "data": []}
    r = requests.request(method, f"{API}/{path}", params=params, timeout=60)
    try:
        j = r.json()
    except Exception:
        raise SystemExit(f"비JSON 응답 {r.status_code}: {r.text[:300]}")
    if r.status_code >= 400 or "error" in j:
        raise SystemExit(f"API 오류 {r.status_code}: {json.dumps(j, ensure_ascii=False)[:500]}")
    return j

def me():
    return _req("GET", "me", fields="user_id,username,followers_count,media_count")

def user_id():
    return os.environ.get("IG_USER_ID") or str(me()["user_id"])

def wait_container(cid, tries=40):
    for _ in range(tries):
        j = _req("GET", cid, fields="status_code,status")
        if j.get("status_code") == "FINISHED":
            return True
        if j.get("status_code") in ("ERROR", "EXPIRED"):
            raise SystemExit(f"컨테이너 실패: {j}")
        time.sleep(5)
    raise SystemExit("컨테이너 타임아웃")

def publish(cid):
    uid = user_id()
    wait_container(cid)
    return _req("POST", f"{uid}/media_publish", creation_id=cid)["id"]

def post_image(url, caption):
    uid = user_id()
    cid = _req("POST", f"{uid}/media", image_url=url, caption=caption)["id"]
    return publish(cid)

def post_carousel(urls, caption):
    uid = user_id()
    children = []
    for u in urls:
        children.append(_req("POST", f"{uid}/media", image_url=u, is_carousel_item="true")["id"])
    for c in children:
        wait_container(c)
    cid = _req("POST", f"{uid}/media", media_type="CAROUSEL", children=",".join(children), caption=caption)["id"]
    return publish(cid)

def post_reel(video_url, caption, share_to_feed=True, trial=False):
    uid = user_id()
    kw = dict(media_type="REELS", video_url=video_url, caption=caption, share_to_feed=str(share_to_feed).lower())
    if trial:
        kw["trial_params"] = json.dumps({"share_to_feed_on_success": True})  # 트라이얼 릴스 (미지원 시 API 오류로 바로 드러남)
    cid = _req("POST", f"{uid}/media", **kw)["id"]
    return publish(cid)

def post_story(image_url=None, video_url=None):
    uid = user_id()
    kw = dict(media_type="STORIES")
    if image_url: kw["image_url"] = image_url
    if video_url: kw["video_url"] = video_url
    cid = _req("POST", f"{uid}/media", **kw)["id"]
    return publish(cid)

def media_insights(media_id, metrics="reach,saved,shares,likes,comments,follows,views"):
    j = _req("GET", f"{media_id}/insights", metric=metrics)
    return {d["name"]: (d.get("values") or [{}])[0].get("value") for d in j.get("data", [])}

def account_insights(days=7):
    uid = user_id()
    since = int(time.time()) - days*86400
    out = {}
    for m, extra in [("reach", {"metric_type":"total_value","breakdown":"follow_type"}), ("follows_and_unfollows", {"metric_type":"total_value"}), ("views", {"metric_type":"total_value"})]:
        try:
            j = _req("GET", f"{uid}/insights", metric=m, period="day", since=since, **extra)
            out[m] = j.get("data")
        except SystemExit as e:
            out[m] = f"err: {e}"
    return out

def recent_media(limit=25):
    uid = user_id()
    return _req("GET", f"{uid}/media", fields="id,caption,media_type,timestamp,permalink,like_count,comments_count", limit=limit).get("data", [])

def comments(media_id):
    return _req("GET", f"{media_id}/comments", fields="id,text,username,timestamp,replies{id,text,username}").get("data", [])

def reply(comment_id, message):
    return _req("POST", f"{comment_id}/replies", message=message)

def refresh_token():
    j = _req("GET", "refresh_access_token", grant_type="ig_refresh_token")
    return j  # {"access_token":..., "expires_in":...}

def publishing_limit():
    uid = user_id()
    return _req("GET", f"{uid}/content_publishing_limit", fields="quota_usage,config")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "me"
    print(json.dumps(globals()[cmd](*sys.argv[2:]), ensure_ascii=False, indent=2))
