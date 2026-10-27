import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # ON 레포 루트
STATE = ROOT / "state"
QUEUE = ROOT / "bot" / "queue.json"
ENV_FILE = ROOT / ".env"                               # git 제외. 토큰은 여기에만 있다
API = "https://graph.instagram.com/v23.0"


def load_env():
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def write_env(key, value):
    """한 줄만 바꿔 쓴다(토큰 자동 갱신용). 임시 파일에 쓰고 원자적으로 교체한다."""
    lines = ENV_FILE.read_text(encoding="utf-8").splitlines() if ENV_FILE.exists() else []
    out, done = [], False
    for line in lines:
        if line.split("=", 1)[0].strip() == key:
            out.append(f"{key}={value}"); done = True
        else:
            out.append(line)
    if not done:
        out.append(f"{key}={value}")
    tmp = ENV_FILE.with_suffix(".tmp")
    tmp.write_text("\n".join(out) + "\n", encoding="utf-8")
    os.replace(tmp, ENV_FILE)
    os.environ[key] = value


load_env()
SHORTS_ROOT = Path(os.environ.get("SHORTS_ROOT", r"D:\쇼츠"))
ASSET_BASE = os.environ.get("ASSET_BASE", "").rstrip("/")   # https://raw.githubusercontent.com/<owner>/<repo>/main
MUSIC_BANK = SHORTS_ROOT / "content" / "music_bank" / "on"
VOICE_MODEL = os.environ.get("ON_VOICE_MODEL", "gemini-3.1-flash-live-preview")   # 하루 무제한(쇼츠공장 실측)
VOICE_NAME = os.environ.get("ON_VOICE_NAME", "Orus")                              # 드림님이 귀로 고른 남성 목소리
DAILY_PUBLISH_MAX = 4          # 30일 스프린트: 하루 릴스 3 + 카드 1. 밀린 건은 사장이 재편성한다(몰아 올리기 금지)
MIN_GAP_HOURS = 3              # 같은 날 발행 사이 최소 간격
SLOT_JITTER_MIN = 20           # 슬롯 시각에 ±20분 (항목마다 고정된 무작위)
TOKEN_REFRESH_DAYS_LEFT = 15   # 만료 15일 전부터 매일 갱신 시도
