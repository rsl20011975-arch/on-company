"""공개 레포·텔레그램으로 나가는 글에서 비밀값을 지운다.

2026-10-30 사고: requests 의 연결 오류 메시지에 요청 URL(access_token 쿼리 포함)이 그대로 실려
health.json 에 커밋됐다. 원인 수리는 ig.req/threads.req 가 URL 을 오류에 싣지 않게 한 것이고,
이 함수는 그 뒤에 남겨 두는 마지막 거름망이다.
"""
import os, re

_SECRET_KEYS = ("IG_ACCESS_TOKEN", "THREADS_ACCESS_TOKEN")


def redact(text):
    text = re.sub(r"(access_token=)[^&\s'\"]+", r"\1***", str(text))
    for k in _SECRET_KEYS:
        v = os.environ.get(k)
        if v and len(v) > 8:
            text = text.replace(v, "***")
    return text
