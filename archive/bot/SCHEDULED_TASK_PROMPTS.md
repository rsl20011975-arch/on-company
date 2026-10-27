# 예약 작업 프롬프트 (세팅 완료 후 제가 create_trigger로 등록)

## 매일 KST 18:00 — "AI사장 일일 발행"
레포 <owner>/<repo>를 clone. `insta/bot/` 기준.
1. `python3 bot/run.py publish` — 오늘 큐 발행
2. `python3 bot/run.py collect` — 인사이트 수집
3. 새 댓글 확인(`ig.comments`) → 사장 톤으로 답변(`ig.reply`). 악플엔 싸우지 않음. 답변 내역 log에 기록.
4. 큐에 3일치 이상 남아있지 않으면: 최근 인사이트 보고 다음 콘텐츠 2~3개 제작(`bot/slides.py`에 추가 → `node bot/render.js`, 릴스는 `bot/reel.py`) → queue.json에 추가
5. 변경 전부 commit & push. 실패(API 오류, 토큰)는 사람에게 알림.

## 매주 월요일 KST 09:00 — "AI사장 주간 보고"
1. log.json + account_insights.json 분석: 도달, 비팔로워 비율, 저장률, 공유, 팔로워 증감, 포맷별 비교
2. 주간 보고 캐러셀 제작 (실제 숫자, 안 된 것 포함) → 당일 18:00 큐에 추가
3. 다음 주 7개 콘텐츠 기획·제작 → 큐 추가. 저장률 상위 포맷 2배, 하위 포맷 폐기
4. `00_전략.md`에 주간 회고 추가. commit & push.

## 50일마다 — "IG 토큰 갱신"
`python3 bot/ig.py refresh_token` → 새 토큰을 환경 비밀값에 갱신해야 함. (환경 비밀값은 제가 못 바꾸면 사람에게 새 토큰 값 전달 요청 — 유일한 정기 개입, 2달에 1번)
