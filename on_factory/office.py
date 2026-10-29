"""사장실(온)이 레포를 만질 때 쓰는 입구. 공장 작업과 같은 레포 잠금을 잡고 git 을 돌린다.

python -m on_factory.office pull
python -m on_factory.office commit "메시지" 경로1 경로2 ...   (add → commit → push)
공장이 30분마다 같은 작업 폴더에서 pull/push 한다. 사장실이 git 을 직접 치면 2026-10-29 13:00 같은 충돌이 난다.
"""
import sys
from . import repo_lock, store

TRAILER = "\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"


def main(argv):
    cmd = argv[0] if argv else ""
    with repo_lock.held(f"사장실 {cmd}"):
        if cmd == "pull":
            store.pull()
        elif cmd == "commit" and len(argv) >= 3:
            store.git("add", *argv[2:])
            if not store.git("diff", "--cached", "--name-only"):
                print("바뀐 것 없음"); return
            store.git("commit", "-m", argv[1] + TRAILER)
            store.git("push", "origin", "main")
        else:
            sys.exit(__doc__)
    print(store.git("log", "--oneline", "-1"))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main(sys.argv[1:])
