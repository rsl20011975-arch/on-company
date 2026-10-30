"""Threads API (graph.threads.net) 클라이언트. ig.py 와 같은 모양: 판단 없이 요청만 한다.

토큰: .env 의 THREADS_ACCESS_TOKEN (aisajang.on 테스터 장기 토큰, 60일). IG_DRY_RUN=1 이면 요청을 찍기만 한다.
공식 문서(2026-10-28 확인): 텍스트 500자, 링크 5개 이하, 컨테이너 생성 → 약 30초 대기 → threads_publish.
영상(2026-10-29 확인): MP4/MOV, H.264, AAC 48kHz 이하, moov 앞, 5분 이하. 캐러셀 2~20장(이미지·영상 혼합 가능).
"""
import json, os, time, urllib.parse
import requests
from .ig import DRY, IGError

API = "https://graph.threads.net/v1.0"
MAX_TEXT = 500


def _token():
    t = os.environ.get("THREADS_ACCESS_TOKEN")
    if not t and not DRY:
        raise IGError("THREADS_ACCESS_TOKEN 없음 (.env)")
    return t or "DRY"


def req(method, path, **params):
    params["access_token"] = _token()
    if DRY:
        print(f"[DRY threads] {method} {path} {json.dumps({k: v for k, v in params.items() if k != 'access_token'}, ensure_ascii=False)[:240]}")
        return {"id": f"dry_{int(time.time()*1000)}", "status": "FINISHED", "data": []}
    try:
        r = requests.request(method, f"{API}/{path}", params=params, timeout=90)
    except requests.RequestException as e:   # 오류 문구에 토큰 붙은 URL 이 실린다 - 그대로 올리지 않는다
        raise IGError(f"Threads 연결 실패 {type(e).__name__} ({method} {path})") from None
    try:
        j = r.json()
    except ValueError:
        raise IGError(f"Threads 비JSON 응답 {r.status_code}: {r.text[:300]}")
    if r.status_code >= 400 or "error" in j:
        raise IGError(f"Threads {r.status_code} {json.dumps(j.get('error', j), ensure_ascii=False)[:400]}")
    return j


def me():
    return req("GET", "me", fields="id,username,name")


def publishing_limit():
    return req("GET", f"{me()['id']}/threads_publishing_limit", fields="quota_usage,config")


def _wait(cid, tries=24):
    for _ in range(tries):
        s = req("GET", cid, fields="status,error_message")
        if s.get("status") == "FINISHED":
            return
        if s.get("status") in ("ERROR", "EXPIRED"):
            raise IGError(f"Threads 컨테이너 {cid} 실패: {s}")
        time.sleep(5)
    raise IGError(f"Threads 컨테이너 {cid} 준비 시간 초과")


def _container(uid, **kw):
    cid = req("POST", f"{uid}/threads", **kw)["id"]
    _wait(cid, tries=60 if kw.get("media_type") == "VIDEO" else 24)   # 영상은 처리 시간이 길다
    return cid


def post(text, reply_to=None, video_url=None, image_urls=None):
    """글 1개. 영상 1개(video_url) 또는 이미지 2~20장(image_urls, 캐러셀)을 붙일 수 있다."""
    if len(text) > MAX_TEXT:
        raise IGError(f"Threads 글 {len(text)}자 (상한 {MAX_TEXT})")
    uid = me()["id"]
    kw = dict(text=text, **({"reply_to_id": reply_to} if reply_to else {}))
    if video_url:
        cid = _container(uid, media_type="VIDEO", video_url=video_url, **kw)
    elif image_urls:
        if not 2 <= len(image_urls) <= 20:
            raise IGError(f"Threads 캐러셀은 2~20장 ({len(image_urls)}장)")
        kids = [_container(uid, media_type="IMAGE", image_url=u, is_carousel_item="true") for u in image_urls]
        cid = _container(uid, media_type="CAROUSEL", children=",".join(kids), **kw)
    else:
        cid = _container(uid, media_type="TEXT", **kw)
    return req("POST", f"{uid}/threads_publish", creation_id=cid)["id"]


def post_text(text, reply_to=None):
    return post(text, reply_to)


def post_thread(parts, video_url=None, image_urls=None):
    """여러 단락을 이어진 스레드(본글 + 자기 답글)로 올린다. 매체는 본글에만 붙는다. 각 단락 500자 이하."""
    ids = [post(parts[0], video_url=video_url, image_urls=image_urls)]
    for p in parts[1:]:
        ids.append(post(p, reply_to=ids[-1]))
    return ids


def insights(media_id):
    return req("GET", f"{media_id}/insights", metric="views,likes,replies,reposts,quotes,shares").get("data", [])


def refresh_token():
    return req("GET", "refresh_access_token", grant_type="th_refresh_token")
