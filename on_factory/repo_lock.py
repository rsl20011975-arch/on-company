"""레포 잠금: 공장 작업(daily·collect·comments)은 한 번에 하나만 레포를 만진다.

2026-10-29 13:00 실측: 스케줄러가 세 작업을 같은 순간에 띄워 같은 작업 폴더에서 git pull 이 겹쳤고,
FETCH_HEAD 가 뒤섞여 "Cannot rebase onto multiple branches" 로 셋 다 실패했다.
잠금 파일은 .git 안에 둔다(추적되지 않는다). 생성 자체가 원자적이라(O_EXCL) 동시에 둘이 잡을 수 없다.
"""
import os, time, contextlib
from .config import ROOT

LOCK = ROOT / ".git" / "on_factory.lock"
WAIT_SEC = 25 * 60       # daily 는 영상 처리 대기로 수 분 걸린다. 다음 tick(30분) 전에는 포기한다
STALE_SEC = 40 * 60      # 이보다 오래된 잠금은 죽은 작업이 남긴 것으로 본다


class Busy(RuntimeError):
    """다른 작업이 레포를 너무 오래 잡고 있다. 이때는 레포를 만지지 않고(생존 신호도 안 쓴다) 알리기만 한다."""


@contextlib.contextmanager
def held(task):
    t0 = time.time()
    while True:
        try:
            fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            try:
                age = time.time() - LOCK.stat().st_mtime
            except FileNotFoundError:      # 확인하는 사이 풀렸다 → 다시 잡는다
                continue
            if age > STALE_SEC:
                print(f"[lock] {int(age)}초 된 잠금을 죽은 작업의 것으로 보고 지운다: {LOCK.read_text(errors='replace')}")
                LOCK.unlink()
                continue
            if time.time() - t0 > WAIT_SEC:
                raise Busy(f"레포 잠금 대기 {WAIT_SEC}초 초과 - 잡고 있는 작업: {LOCK.read_text(errors='replace')}")
            time.sleep(5)
    os.write(fd, f"{task} pid={os.getpid()} at={time.strftime('%H:%M:%S')}".encode())
    os.close(fd)
    try:
        yield
    finally:
        LOCK.unlink()
