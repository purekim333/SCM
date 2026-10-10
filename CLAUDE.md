# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 학습 규칙 (최우선)

- 에이전트 루프와 핵심 로직은 사용자가 직접 작성한다.
- 질문을 받으면 설명과 힌트를 먼저 주고, 사용자가 요청하기 전에는 코드를 대신 쓰지 않는다.
- 리뷰 요청 시 문제점과 이유를 설명하되 수정은 사용자가 한다.
- 세션 시작 시 `docs/PROGRESS.md`를 읽고 현재 상태와 다음 할 일을 확인한다.

## 프로젝트 목적

사용자(yoon)가 SCM 프로그래밍 역량을 키우기 위해 직접 구현하며 배우는 학습 프로젝트.
제조 SCM 데이터를 대상으로, 프레임워크 없이 Anthropic SDK의 tool use만으로 AI 에이전트를 만든다. (기간: 약 3개월)

## 기술 스택

- Python, MySQL, Anthropic SDK
- 에이전트 프레임워크(LangChain 등)는 사용하지 않는다.
- 실제 회사 데이터는 사용하지 않고, 가짜 데이터로만 작업한다.

## Environment

`.env.example`을 `.env`로 복사한 뒤 `DB_USERNAME`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`, `ANTHROPIC_API_KEY`를 채운다.
`.env`와 `.env.*`는 gitignore 대상이다 (`.env.example` 제외). 비밀 정보는 절대 커밋하지 않는다.

## Database

`db/schema.sql`은 파괴적이고 멱등적이다. 뷰와 테이블을 DROP한 뒤 다시 생성하므로, 재실행하면 모든 데이터가 삭제된다.
DROP 순서는 의존성 역순을 지킨다: `component_receipts` → `bom_items` → `plant_capacities` → `supply_plans` → 뷰 → `order_snapshots` → `orders`.
뷰(`vw_order_progress`, `vw_order_delay`)는 계획만 있고 아직 정의하지 않았다. 추가할 때는 테이블 생성 이후에 정의한다.

### 설계 원칙

- 약속(`orders`), 계획(`supply_plans`), 사실(`order_snapshots`)을 분리한다.
- 특별한 의도가 없다면, 현상(인터페이스로 받은 데이터)을 그대로 DB에 담고 판단은 계산으로 꺼낸다.

### Data model

- `orders`: 오더 라인당 한 행 (PK `sales_order`, `sales_order_item`).
  생산 공장, 납품처, 자재, `order_qty`와 리드타임 역산으로 연결된 세 개의 납기를 가진다:
  `rqst_date`(납품요청일) ← `ship_need_date`(운송 리드타임을 고려한 선적필요일, 예: 미국 약 3개월) ← `prod_need_date`(생산필요일).
  `order_date`(수주일)도 가진다. 고객 리드타임(`rqst_date - order_date`)이 표준 납기보다 짧으면 긴급 오더다.
  긴급 여부는 컬럼으로 저장하지 않고 계산으로 판단한다. 표준 납기와 긴급 비율 값은 시드 스크립트 상수를 따른다.
- `order_snapshots`: 일별 인터페이스 상태를 그대로 쌓음 (PK에 `cut_off_date` 추가).
  `prod_qty`, `carry_over_qty`, `stuffing_qty`(컨테이너 적입 수량)는 그날 해당 단계에 머물러 있는 수량,
  `ship_qty`는 누적 출하 수량.
- `supply_plans`: 계획 월 × 오더 라인당 한 행 (PK `plan_month`, `sales_order`, `sales_order_item`). `plan_month`는 매월 1일.
  `demand_qty`는 그 달에 반영해야 할 수량으로, 첫 달은 `order_qty`, 이후는 전월 `carry_over_qty`다.
  항상 `prod_qty + carry_over_qty = demand_qty`. `carry_over_qty`는 공정 단계가 아니라 다음 달로 넘어간 미반영 수량이다.
  `short_reason`은 미반영 사유 코드(`CAPA`, `MATERIAL`, 없으면 NULL). `order_qty`는 의도적 반정규화라 `orders`와 일치 검증이 필요하다.
  그 달 계획 확정일(생산반영일) 이전에 수주된 오더만 그 달 계획 대상이 된다. 확정일 이후 수주는 다음 달로 밀린다.
  생산반영일은 전월 말일부터 거꾸로 센 5번째 영업일이다 (주말만 제외, 공휴일 무시. 말일이 평일이면 말일이 1번째). 예: 2월 계획은 1/26에 확정.
  배분 우선순위는 전월 이월분 먼저, 그다음 `prod_need_date` 빠른 순이며, 캐파를 남김없이 쓰는 부분 반영을 허용한다.
- `plant_capacities`: 공장 × 계획 월당 한 행 (PK `plan_month`, `plant`). `capa_qty`는 월 생산 가능 수량(대).
  수요가 없는 달도 이월분이 떨어질 수 있으므로 매달 행을 둔다. 시드는 1120 광주공장 월 2,000대.
- `bom_items`: 완제품 × 부품당 한 행 (PK `mtrl_code`, `component_code`). `component_qty_per_unit`은 완제품 1대당 부품 소요량. 1단계 BOM만 다룬다.
- `component_receipts`: 부품 입고(GR) 문서 아이템당 한 행 (PK `gr_no`, `gr_item`). 헤더 정보(입고일, 공장, 협력사)는 아이템마다 반복해서 담는다.
  입고는 일별 현상 그대로 담고, 월 가용량은 `SUM`으로 계산한다.

### Supply plan rule

- 그달 생산 한도 = min(캐파, 자재로 만들 수 있는 대수).
- 이월이 생기면 더 작은 쪽이 사유다. 자재 쪽이 작으면 `MATERIAL`, 캐파 쪽이 작으면 `CAPA`, 같으면 `MATERIAL`.
- 시뮬레이션은 전월 `supply_plans`의 이월분을 읽으므로 첫 달부터 순서대로 실행한다.
- 실행 순서: `db/schema.sql` → `script/seed_order_data.py` → `script/seed_plant_capacities.py` → `script/simulate_supply_plans.py`. 모든 스크립트는 멱등이다.

### Delay rule (시점 기준)

`ship_need_date` 시점의 스냅샷에서 `ship_qty < order_qty`이면 지연.
완료된 오더는 전량 도달한 첫 `cut_off_date > ship_need_date`와 결과가 같다.

### 미결 사항

- 스냅샷의 `order_qty` 유지 여부 (주문 변경 이력 추적 필요성 검토 중)
- `ship_need_date`에 스냅샷이 없을 때의 판단 기준 (현재 가정: 그 이전 가장 최근 스냅샷)
- 테이블 간 외래키 추가 (현재 FK, NOT NULL, CHECK 제약 없음)
- 헤더/아이템 분리, 마스터 테이블 등 실무형 스키마 정비 (#18)
- `short_reason` 코드의 의미는 코드 테이블로 옮길 예정

스키마 주석은 한국어로 작성한다.

## Git workflow

- GitHub Flow: `main`은 항상 동작하는 상태로 유지하고, 모든 작업은 브랜치에서 한 뒤 PR로 머지한다.
- 브랜치 접두어: `feat/`, `fix/`, `docs/`, `chore/` + kebab-case (예: `feat/seed-fake-data`)
- 커밋 메시지: Conventional Commits + 한국어 설명 (예: `feat: 오더 및 일별 스냅샷 테이블 스키마 추가`)
- PR 설명에는 무엇 / 왜 / 어떻게 확인했는지를 적고, 관련 이슈는 `Closes #번호`로 연결한다.