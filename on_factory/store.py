"""상태 파일과 git 동기화. 상태는 전부 레포의 state/ 에 있고, 바뀔 때마다 바로 push 한다(이사회 P0 #4)."""
import json, subprocess, datetime as dt
from .config import ROOT, STATE

KST = dt.timezone(dt.timedelta(hours=9))


def now():
    return dt.datetime.now(KST)


def load(name, default):
    p = STATE / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


def save(name, obj):
    STATE.mkdir(exist_ok=True)
    p = STATE / name
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(p)


def git(*args, check=True):
    r = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and r.returncode:
        raise RuntimeError(f"git {' '.join(args)} 실패: {r.stderr.strip()[:300]}")
    return r.stdout.strip()


def pull():
    git("pull", "--rebase", "--autostash", "origin", "main")


def push(msg, paths=("state",)):
    git("add", *paths)
    if not git("status", "--porcelain", *paths):
        return False
    git("commit", "-m", f"factory: {msg}")
    for attempt in range(3):
        r = subprocess.run(["git", "-C", str(ROOT), "push", "origin", "main"], capture_output=True, text=True)
        if r.returncode == 0:
            return True
        git("pull", "--rebase", "origin", "main", check=False)
    raise RuntimeError("push 3회 실패 - 상태가 원격에 기록되지 않았다. 다음 발행을 멈춘다")
