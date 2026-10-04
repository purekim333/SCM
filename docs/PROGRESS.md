# Progress

## 목표
SCM 챗봇에 질문하면 **DB 구조 파악 → SQL 생성 → 웹 서치 → 인사이트 있는 답변**까지 해 주는 에이전트를 만든다.
(단순 RAG 챗봇과 다른 점: 문서 검색이 아니라 실제 데이터를 조회해서 답한다)

## 현재 상태 (2026-10-03)
- [x] Python venv, requirements.txt, `.env` 기반 DB 연결
- [x] `orders` / `order_snapshots` 스키마
- [x] 오더 시드 221건 생성 (`script/seed_order_data.py`, 멱등·재현 가능)
- [x] 검증 쿼리 3종 (`db/verify_orders.sql`)
- [x] PR #9 머지 → 이슈 #2 종료

## 다음 할 일
1. PR #9 정리 커밋(주석, 변수명, 매직 넘버) → 셀프 리뷰 → 머지
2. 2주차: `order_snapshots` 일별 시뮬레이션 설계

## 고민 중 / 나중에 할 것
- 리드타임을 권역별·자재별 마스터 테이블로 → #8
- 시드 INSERT가 한 행씩 왕복해서 느리다 → 측정 후 executemany / chunk 검토
- `orders` ↔ `order_snapshots` 외래키 (6주차에 재논의)
- 자재·수량·납품처도 랜덤으로

## 로그
### 2026-10-03
**한 일**
- 납품요청일 랜덤 → 선적필요일, 생산필요일 역산 (`datetime`, `timedelta`)
- 오더별 아이템 수 랜덤, 40개 오더로 221건
- 검증 쿼리를 `.sql` 파일로 모음, 이슈 #8 열고 PR #9 생성
- 시드 파일명 `git mv`로 snake_case 변경
- supply plan 스키마 생성

**배운 것**
- 약속(납품요청일)은 정해지고, 나머지는 리드타임으로 계산된다
- 재현성(seed) ≠ 멱등성(TRUNCATE 후 INSERT)
- "어긴 것만 보여주고 0행이면 통과" 검증 패턴, `HAVING`, `CASE WHEN`, `COUNT(DISTINCT)`
- `only_full_group_by`: GROUP BY에 없는 컬럼은 집계 함수로 감싼다
- Windows mysql 한글 깨짐 = UTF-8 vs CP949 → `--default-character-set=utf8mb4`
- 더 좋은 설계가 보이면 그 자리에서 고치지 말고 이슈로 빼기
- 비밀번호는 채팅·로그에 절대 붙여 넣지 않기

### 2026-10-02
**한 일**
- 중첩 반복문으로 오더 100건, 오더번호 zero-padding (`f"S{order:05}"`)

**배운 것**
- `range`는 끝값을 포함하지 않는다 (off-by-one)
- 결과는 전부 찍지 말고 `COUNT(*)`로 확인
- 커밋 하나에는 주제 하나

### 2026-10-01
**한 일**
- Python 초기 세팅과 MySQL 설정을 README에 반영
- 멱등성을 고려한 시드 데이터 INSERT

**배운 것**
- pymysql은 커넥션에서 `commit()`해야 반영된다
- 트랜잭션과 커밋 원자성을 항상 염두
- TRUNCATE(빠름, 롤백 불가) vs DELETE

### 2026-09-30
**한 일**
- CLAUDE.md 작성, PATH 설정

**정한 것**
- 지연 기준: 선적필요일 시점에 `ship_qty < order_qty`이면 지연 (약속한 날까지 오더 수량을 다 출하하지 못함)