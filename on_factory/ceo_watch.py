"""사장 출근이 끊겼는지 본다. 사장실 커밋(= 'factory:' 로 시작하지 않는 커밋)이 CEO_SILENT_HOURS 넘게 없으면
주주에게 하루 1회 알린다. 공장은 PC 가 켜져 있으면 돌지만, 사장(Claude 데스크톱 앱의 예약 작업)은 앱이 꺼지면 조용히 멈춘다.
2026-10-30 15:55 ~ 11-01 14:39 출근 5회가 아무 신호 없이 빠졌다 - 발행 대기분이 남아 있어 runway 경보도 울리지 않았다."""
import datetime as dt
from . import store
from .notify import send

CEO_SILENT_HOURS = 16   # 정상 밤 공백(20시 출근 커밋 → 다음 10시 출근 커밋)이 14~15시간이다. 16시간 = 그다음 출근 1회 이상 결근


def last_ceo_commit():
    out = store.git("log", "-1", "--format=%cI", "--invert-grep", "--grep=^factory:")
    return dt.datetime.fromisoformat(out) if out else None


def run():
    now = store.now()
    if not 10 <= now.hour < 22:          # 밤에는 원래 출근이 없다
        return
    last = last_ceo_commit()
    silent = (now - last).total_seconds() / 3600 if last else None
    w = store.load("ceo_watch.json", {})
    w.update(checked_at=now.isoformat(), last_ceo_commit=last.isoformat() if last else None,
             silent_hours=round(silent, 1) if silent is not None else None)
    if (silent is None or silent >= CEO_SILENT_HOURS) and w.get("alerted") != now.date().isoformat():
        send(f"ON 사장 온의 마지막 출근 기록이 {w['silent_hours']}시간 전이다. 발행은 공장이 계속하지만 새 콘텐츠 제작이 멈췄다 - "
             "Claude 데스크톱 앱이 켜져 있는지만 확인해 주세요. 내용 판단은 필요 없다.")
        w["alerted"] = now.date().isoformat()
    store.save("ceo_watch.json", w)
