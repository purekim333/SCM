# Progress

## 목표
SCM 챗봇에 질문하면 **DB 구조 파악 → SQL 생성 → 웹 서치 → 인사이트 있는 답변**까지 해 주는 에이전트를 만든다.
(단순 RAG 챗봇과 다른 점: 문서 검색이 아니라 실제 데이터를 조회해서 답한다)

## 현재 상태 (2026-10-10)

### 1주차: 오더 가짜 데이터 ✅
- [x] Python venv, requirements.txt, `.env` 기반 DB 연결
- [x] `orders` / `order_snapshots` 스키마
- [x] 오더 시드 (`script/seed_order_data.py`, 멱등·재현 가능)
- [x] 검증 쿼리 3종 (`db/verify_orders.sql`)
- [x] PR #9 머지 → 이슈 #2 종료

### 2주차: 공급계획 시뮬레이션 (상위 이슈 #10, 브랜치 `feat/supply-plan-simulation`)
- [x] `orders.order_date`(수주일) 추가, 긴급 오더 약 10% → 시드 결과 **207건** (예전 221건은 수주일 추가 전 숫자)
- [x] `supply_plans`, `plant_capacities` 스키마
- [x] 캐파 시드: 1120 광주공장 월 2,000대, 2024-11 ~ 2028-03 41행 (`script/seed_plant_capacities.py`)
- [x] #11 DB 접속 코드를 `script/db.py` 하나로
- [x] #12 시드 스크립트 함수화, `month_range` (`script/date_utils.py`)
- [x] #13 pytest 도입, `month_range` 테스트 5건
- [x] #14 생산반영일 `plan_lock_date` (월말에서 5번째 영업일) + 테스트
- [x] #15 월별 공급계획 시뮬레이션: 313행 (사유 NULL 207, CAPA 106), `SUM(prod_qty) = SUM(order_qty) = 41,400`, 멱등, 긴급 오더 S00135는 3월 계획에만 등장
- [ ] #16 자재 부족 시나리오 (short_reason = MATERIAL) ← 진행 중
  - [x] `bom_items`, `component_receipts` 스키마 (72e47ef)
  - [x] 사유 규칙 확정: 그달 한도 = min(캐파, 자재로 만들 수 있는 대수). 더 작은 쪽이 사유, 같으면 `MATERIAL`
  - [x] 입고 규칙 확정: 주간 랜덤 입고, `random.seed(42)`
  - [ ] `script/seed_components.py` (BOM + 부품 입고 시드)
  - [ ] 시뮬레이션에 자재 한도 반영
- [ ] #17 공급계획 검증 SQL (라인별 `SUM(prod_qty) = order_qty`, 불변식 `prod + carry_over = demand`, 반정규화 `order_qty` 일치)
- [ ] PR (Closes #10)

## 다음 할 일
1. #16 `seed_components.py` → 시뮬레이션 자재 한도 → MATERIAL 이월 확인
2. #17 검증 SQL → PR
3. 일요일: 주간 회고 + 블로그 #2 (공급계획 시뮬레이션)
4. 3주차: 일별 `order_snapshots` → `vw_order_delay` + Anthropic SDK 첫 호출 → M0(10/16) 출하 지연 사슬을 손 SQL로

## 고민 중 / 나중에 할 것
- #18 실무형 스키마 정비 (헤더/아이템, 마스터 테이블, 제약)
- 리드타임을 권역별·자재별 마스터 테이블로 → #8
- 시드 INSERT가 한 행씩 왕복해서 느리다 → 측정 후 executemany / chunk 검토
- 시뮬레이션 루프를 fetch / plan / insert 함수로 쪼개기, `prev_plan_month` 중복, `capa_record` → `capa_qty` 이름 정리
- `CAPA_SQL`에 plant 조건 없음 (지금은 공장 1개 가정)
- `script/`에 라이브러리와 실행 파일이 섞여 있음 → M1 전에 패키지 구조 개편
- `orders` ↔ `order_snapshots` 외래키 (6주차에 재논의)
- 수량·납품처·자재도 랜덤으로 (지금은 전부 200대, 전기자전거 한 종류)

## 로그
### 2026-10-10
**한 일**
- #15 월별 공급계획 시뮬레이션 루프 완성 (009c974): 이월분 먼저, 생산필요일 순으로 캐파 배분
- 신규 수요 = 생산필요일이 다음 달 1일 전 + 수주일이 반영일 이전 + 아직 계획에 없는 것(`NOT EXISTS`), 이월 수요 = 전월 `carry_over_qty > 0`. `UNION ALL` + priority로 정렬
- 결과 검증: 313행, `SUM(prod_qty) = SUM(order_qty) = 41,400`, 다시 돌려도 같은 결과
- #16 설계: BOM과 부품 입고를 테이블로, `bom_items`, `component_receipts` 스키마 추가 (72e47ef)

**배운 것**
- 수요를 "생산필요일이 그 달 안"으로만 뽑으면 반영일 이후 들어온 긴급 오더(S00135)가 영원히 사라진다
- 이월은 매달 새 행으로 이어 붙는 사슬이고, 이 사슬이 챗봇이 "왜 늦었어?"에 답하는 증거가 된다
- 부품을 컬럼으로 두면 부품이 바뀔 때 확장이 어렵다 → 부품을 행으로 (제1정규형), 1대당 소요량 컬럼
- 입고는 월마다 받는 게 아니다 → 현상(일별 입고)은 그대로 담고, 월 가용량은 `SUM`으로 계산
- 자재 부족의 근거도 캐파처럼 DB에 있어야 챗봇이 "얼마나 부족했는데?"에 답할 수 있다

### 2026-10-09
**한 일**
- #11 DB 접속 코드를 `script/db.py`로 모음 (10/8)
- #12 `month_range` (끝 월 포함), 시드 스크립트를 함수 + `__main__`으로
- #13 pytest 도입, `month_range` 테스트 5건 → 거꾸로 된 기간 버그 발견, `ValueError`로 막음
- #14 생산반영일 `plan_lock_date` TDD (1·2·4·5·9월 parametrize)
- #15 `plan_one_month` 순수 함수 + 테스트 (부분 반영, 캐파 = 수요 경계값)

**배운 것**
- `relativedelta(month=6)`은 바꾸기, `months=6`은 더하기. 에러 없이 틀린다 → 검증 쿼리로 커밋 전에 잡기
- 일하는 코드는 함수 안, 부르는 건 `__main__`에서만 (import만 해도 맨 위 코드는 실행된다)
- 테스트가 실패하면 "코드가 틀렸나, 테스트가 틀렸나"부터 구분
- 경계값 분석: 생산반영일의 경계는 "말일의 요일" 7가지
- `pip freeze`는 개발 도구까지 섞는다 → 의존성은 `requirements.txt` / `requirements-dev.txt`에 손으로

### 2026-10-04 ~ 10-07
**한 일**
- `orders.order_date`(수주일) 추가, 긴급 오더 10% (일반 오더는 납품요청일 130일 이상 전에 수주)
- `plant_capacities` 테이블, 월별 수요 분석 쿼리(`db/analyze_monthly_demand_qty.sql`)로 캐파 2,000대 결정
- 캐파 시드 41행 (bae9fe7)

**배운 것**
- 수주 여유의 기준은 생산이 아니라 계획 확정일(반영일)
- 긴급 여부는 컬럼(`is_urgent`)이 아니라 계산으로 (현상은 그대로, 판단은 계산)
- 캐파는 지연 원인의 증거라 상수가 아니라 테이블에
- 수요(만들어야 함)와 캐파(만들 수 있음)는 다른 개념
- 첫 윈도우 함수 `SUM(...) OVER ()`

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