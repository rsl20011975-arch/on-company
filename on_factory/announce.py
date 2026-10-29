"""발행 즉시 보고. 인스타·Threads 게시가 끝나면 그 자리에서 텔레그램으로 1건 보낸다(2026-10-29 개입 23번 "발행되면 그때마다 보고해").

게시는 이미 끝난 뒤라, 링크를 못 읽거나 전송이 실패해도 발행 기록을 되돌리지 않는다 - 실패는 로그와 메시지 안에 그대로 남긴다.
"""
from . import ig, threads
from .notify import send


def _link(api, mid):
    try:
        return api.req("GET", mid, fields="permalink").get("permalink", "(링크 없음)")
    except Exception as e:
        return f"(링크 못 읽음: {type(e).__name__})"


def published(platform, slug, mid, what=""):
    api = ig if platform == "인스타" else threads
    text = f"발행 완료 - {platform} {slug}{' (' + what + ')' if what else ''}\n{_link(api, mid)}"
    if not send(text):
        print(f"[발행 보고 전송 실패] {text}")
