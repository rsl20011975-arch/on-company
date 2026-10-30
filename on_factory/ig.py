"""Instagram API (Instagram Login, graph.instagram.com) 클라이언트."""
import json, os, time
import requests
from .config import API

DRY = os.environ.get("IG_DRY_RUN") == "1"


class IGError(RuntimeError):
    pass


def _token():
    t = os.environ.get("IG_ACCESS_TOKEN")
    if not t and not DRY:
        raise IGError("IG_ACCESS_TOKEN 없음 (.env)")
    return t or "DRY"


def req(method, path, **params):
    params["access_token"] = _token()
    if DRY:
        print(f"[DRY] {method} {path} {json.dumps({k: v for k, v in params.items() if k != 'access_token'}, ensure_ascii=False)[:240]}")
        return {"id": f"dry_{int(time.time()*1000)}", "user_id": "dry_uid", "status_code": "FINISHED", "data": [], "expires_in": 5184000}
    try:
        r = requests.request(method, f"{API}/{path}", params=params, timeout=90)
    except requests.RequestException as e:   # 오류 문구에 토큰 붙은 URL 이 실린다 - 그대로 올리지 않는다
        raise IGError(f"연결 실패 {type(e).__name__} ({method} {path})") from None
    try:
        j = r.json()
    except ValueError:
        raise IGError(f"비JSON 응답 {r.status_code}: {r.text[:300]}")
    if r.status_code >= 400 or "error" in j:
        raise IGError(f"{r.status_code} {json.dumps(j.get('error', j), ensure_ascii=False)[:400]}")
    return j


def me():
    return req("GET", "me", fields="user_id,username,followers_count,media_count")


def uid():
    return os.environ.get("IG_USER_ID") or str(me()["user_id"])


def wait_ready(cid, tries=60):
    for _ in range(tries):
        s = req("GET", cid, fields="status_code,status").get("status_code")
        if s == "FINISHED":
            return
        if s in ("ERROR", "EXPIRED"):
            raise IGError(f"컨테이너 {cid} 실패: {s}")
        time.sleep(5)
    raise IGError(f"컨테이너 {cid} 준비 시간 초과")


def _publish(cid):
    wait_ready(cid)
    return req("POST", f"{uid()}/media_publish", creation_id=cid)["id"]


def _check_jpeg(url):
    # 인스타 API 이미지 발행은 JPEG 만 받는다(이사회 P0 #1). 확장자로 1차 차단.
    if not url.split("?")[0].lower().endswith((".jpg", ".jpeg")):
        raise IGError(f"JPEG 아님: {url}")


def post_carousel(urls, caption):
    u = uid()
    kids = []
    for url in urls:
        _check_jpeg(url)
        kids.append(req("POST", f"{u}/media", image_url=url, is_carousel_item="true")["id"])
    for k in kids:
        wait_ready(k)
    cid = req("POST", f"{u}/media", media_type="CAROUSEL", children=",".join(kids), caption=caption)["id"]
    return _publish(cid)


def post_image(url, caption):
    _check_jpeg(url)
    return _publish(req("POST", f"{uid()}/media", image_url=url, caption=caption)["id"])


def post_reel(video_url, caption, trial=False, cover_url=None):
    kw = dict(media_type="REELS", video_url=video_url, caption=caption)
    if trial:
        # 공식 스펙: trial_params.graduation_strategy = MANUAL | SS_PERFORMANCE (이사회 P0 #2).
        # API 로는 수동 졸업을 못 하므로 성과 기반 자동 졸업에 맡긴다. share_to_feed 는 보내지 않는다.
        kw["trial_params"] = json.dumps({"graduation_strategy": "SS_PERFORMANCE"})
    else:
        kw["share_to_feed"] = "true"
    if cover_url:
        kw["cover_url"] = cover_url
    return _publish(req("POST", f"{uid()}/media", **kw)["id"])


def post_story(image_url=None, video_url=None):
    kw = dict(media_type="STORIES")
    if image_url:
        _check_jpeg(image_url); kw["image_url"] = image_url
    if video_url:
        kw["video_url"] = video_url
    return _publish(req("POST", f"{uid()}/media", **kw)["id"])


def recent_media(limit=30):
    return req("GET", f"{uid()}/media", fields="id,caption,media_type,media_product_type,timestamp,permalink", limit=limit).get("data", [])


# 미디어 유형별 지표 (이사회 P0 #7). 하나씩 불러 실패한 지표만 따로 기록한다.
METRICS = {
    "REELS": ["views", "reach", "saved", "shares", "likes", "comments", "total_interactions",
              "ig_reels_avg_watch_time", "ig_reels_video_view_total_time"],
    "CAROUSEL_ALBUM": ["views", "reach", "saved", "shares", "likes", "comments", "total_interactions", "follows", "profile_visits"],
    "IMAGE": ["views", "reach", "saved", "shares", "likes", "comments", "total_interactions", "follows", "profile_visits"],
}


def media_insights(media_id, kind):
    out, errs = {}, {}
    for m in METRICS.get(kind, METRICS["IMAGE"]):
        try:
            d = req("GET", f"{media_id}/insights", metric=m).get("data", [])
            out[m] = (d[0].get("values") or [{}])[0].get("value") if d else None
        except IGError as e:
            errs[m] = str(e)[:160]
    return out, errs


def account_daily(metric, since, until, **extra):
    return req("GET", f"{uid()}/insights", metric=metric, period="day", since=since, until=until, **extra).get("data", [])


def comments(media_id):
    return req("GET", f"{media_id}/comments", fields="id,text,username,timestamp,replies{id,username}").get("data", [])


def reply(comment_id, message):
    return req("POST", f"{comment_id}/replies", message=message)


def refresh_token():
    return req("GET", "refresh_access_token", grant_type="ig_refresh_token")


def publishing_limit():
    return req("GET", f"{uid()}/content_publishing_limit", fields="quota_usage,config")
