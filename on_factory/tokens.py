"""토큰 만료 추적과 자동 갱신(인스타·Threads). 새 토큰은 로컬 .env 에만 쓴다(레포에는 만료일만)."""
import datetime as dt
import os
from . import ig, threads, store
from .config import write_env, TOKEN_REFRESH_DAYS_LEFT

# 이름 -> (상태 파일, .env 키, 갱신 함수). Threads 는 2026-10-28 발급(aisajang.on 테스터 장기 토큰, 60일).
KINDS = {
    "instagram": ("token_meta.json", "IG_ACCESS_TOKEN", ig.refresh_token),
    "threads": ("threads_token_meta.json", "THREADS_ACCESS_TOKEN", threads.refresh_token),
}


def refresh(kind):
    meta_file, env_key, do_refresh = KINDS[kind]
    if not os.environ.get(env_key) and not ig.DRY:
        return None                               # 그 토큰을 아직 안 쓰는 단계면 건너뛴다
    meta = store.load(meta_file, {})
    if not meta:                                  # 첫 실행: 방금 발급한 60일 토큰으로 본다(발급 24시간 전엔 갱신 불가)
        meta = {"expires_at": (store.now() + dt.timedelta(days=59)).isoformat(), "assumed": True}
        store.save(meta_file, meta); store.push(f"{kind} token meta init")
    exp = meta.get("expires_at")
    left = (dt.datetime.fromisoformat(exp) - store.now()).days if exp else 0
    if exp and left > TOKEN_REFRESH_DAYS_LEFT:
        return left
    try:
        j = do_refresh()                          # 발급 24시간 이후부터, 유효한 동안만 가능
    except ig.IGError as e:
        if left <= 7:
            from .notify import send
            send(f"{kind} 토큰 갱신 실패, 만료까지 {left}일 - {e}")
        return left
    if j.get("access_token"):
        write_env(env_key, j["access_token"])
    meta = {"refreshed_at": store.now().isoformat(),
            "expires_at": (store.now() + dt.timedelta(seconds=int(j.get("expires_in", 0)))).isoformat()}
    store.save(meta_file, meta); store.push(f"{kind} token refreshed")
    return int(j.get("expires_in", 0)) // 86400


def run():
    return {kind: refresh(kind) for kind in KINDS}
