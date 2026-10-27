"""토큰 만료 추적과 자동 갱신. 새 토큰은 로컬 .env 에만 쓴다(레포에는 만료일만)."""
import datetime as dt
from . import ig, store
from .config import write_env, TOKEN_REFRESH_DAYS_LEFT


def run():
    meta = store.load("token_meta.json", {})
    if not meta:                                  # 첫 실행: 방금 발급한 60일 토큰으로 본다(발급 24시간 전엔 갱신 불가)
        meta = {"expires_at": (store.now() + dt.timedelta(days=59)).isoformat(), "assumed": True}
        store.save("token_meta.json", meta); store.push("token meta init")
    exp = meta.get("expires_at")
    left = (dt.datetime.fromisoformat(exp) - store.now()).days if exp else 0
    if exp and left > TOKEN_REFRESH_DAYS_LEFT:
        return left
    try:
        j = ig.refresh_token()                    # 발급 24시간 이후부터 가능, 유효한 동안만 가능
    except ig.IGError as e:
        if left <= 7:
            from .notify import send
            send(f"토큰 갱신 실패, 만료까지 {left}일 - {e}")
        return left
    if j.get("access_token"):
        write_env("IG_ACCESS_TOKEN", j["access_token"])
    meta = {"refreshed_at": store.now().isoformat(),
            "expires_at": (store.now() + dt.timedelta(seconds=int(j.get("expires_in", 0)))).isoformat()}
    store.save("token_meta.json", meta); store.push("token refreshed")
    return int(j.get("expires_in", 0)) // 86400
