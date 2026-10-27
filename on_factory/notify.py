"""알림은 쇼츠공장의 텔레그램 통로를 그대로 쓴다(평문 전송, 2026-09-28 수정본)."""
import sys
from .config import SHORTS_ROOT


def send(text):
    text = "[ON 공장] " + text
    try:
        sys.path.insert(0, str(SHORTS_ROOT))
        from shared.tools.notify import send as tg
        return tg(text)
    except Exception as e:
        print(f"[알림 실패 {e}] {text}")
        return False
