# PC 세션 인수인계 (사장실 → PC의 Claude)

너는 ON Company의 **PC 실행 담당**이다. 사장은 클라우드에서 일하는 AI 사장 "온"이고, 결정은 이미 이 레포 문서에 전부 적혀 있다.
**너는 새로 판단하지 않는다.** 지시서 값 그대로 실행하고, 결과를 기록한다. 지시서와 화면이 맞지 않으면 멈추고 사람에게 스크린샷을 요청한다.

## 읽을 것
1. `00_온컴퍼니_운영설계서.md` 의 2장(두 층 구조)과 10장(사람 개입 계약서) — 배경만 파악
2. `05_완전자동화_세팅_한번만.md` — **실행할 지시서**

## 할 일 (지시서 순서)
1. 레포가 `D:\on-company` 에 있는지 확인. 없으면 `git clone https://github.com/rsl20011975-arch/on-company D:\on-company`. 작업은 그 폴더에서 한다.
2. 지시서 2번: 인스타그램 계정 (브라우저로 진행, 크롬 연결 필요)
3. 지시서 3번: Meta 앱 `ON Company` 와 토큰 → `D:\on-company\.env` 작성
4. 지시서 4번: 쇼츠공장(`D:\쇼츠`)에 `integration\short-project_on_factory.patch` 적용, `content\schedule.json` 에 `integration\schedule_additions.json` 세 항목 추가
   - 쇼츠공장 CLAUDE.md 의 교훈대로, schedule.json 을 고치기 전에 기존 값을 먼저 읽고, 세 항목은 `"enabled": false` 로 넣는다. 켜는 것은 사장실이 출시 관문 통과 후 지시한다.
5. 지시서 5번: `python shared/lyria/bank.py on --n 6` (쇼츠공장 폴더에서)
6. 지시서 6번: `python D:\on-company\on_factory\run.py check`

## 절대 하지 않는 것
- 비밀번호·인증 코드 입력 (사람이 직접 한다. 화면에서 그 칸이 나오면 멈추고 사람에게 넘긴다)
- 토큰 값을 채팅·파일(.env 제외)·커밋에 남기기
- 인스타에서 팔로우·좋아요·댓글·게시
- 지시서 값 변경, 레포의 운영 문서 수정

## 끝나면
`reports/setup_D-0.md` 를 만들어 아래만 적고 커밋·push 한다 (토큰·비밀번호·메일 주소는 적지 않는다):
- 실제로 된 인스타 아이디
- 각 단계 성공/실패, 실패면 화면에 나온 오류 문구 그대로
- `run.py check` 출력 (계정 정보와 발행 한도 부분만)
그다음 사람에게 "클라우드 세션에 '세팅 끝'이라고 전해 달라"고 말한다.
