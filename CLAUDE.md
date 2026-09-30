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
DROP 순서는 의존성 역순을 지킨다: 뷰 → `order_snapshots` → `orders`.
뷰(`vw_order_progress`, `vw_order_delay`)는 계획만 있고 아직 정의하지 않았다. 추가할 때는 테이블 생성 이후에 정의한다.

### 설계 원칙

- 약속(orders)과 사실(order_snapshots)을 분리한다.
- 특별한 의도가 없다면, 현상(인터페이스로 받은 데이터)을 그대로 DB에 담고 판단은 계산으로 꺼낸다.

### Data model

- `orders`: 오더 라인당 한 행 (PK `sales_order`, `sales_order_item`).
  생산 공장, 납품처, 자재, `order_qty`와 리드타임 역산으로 연결된 세 개의 납기를 가진다:
  `rqst_date`(납품요청일) ← `ship_need_date`(운송 리드타임을 고려한 선적필요일, 예: 미국 약 3개월) ← `prod_need_date`(생산필요일).
- `order_snapshots`: 일별 인터페이스 상태를 그대로 쌓음 (PK에 `cut_off_date` 추가).
  `prod_qty`, `carry_over_qty`, `stuffing_qty`(컨테이너 적입 수량)는 그날 해당 단계에 머물러 있는 수량,
  `ship_qty`는 누적 출하 수량.

### Delay rule (시점 기준)

`ship_need_date` 시점의 스냅샷에서 `ship_qty < order_qty`이면 지연.
완료된 오더는 전량 도달한 첫 `cut_off_date > ship_need_date`와 결과가 같다.

### 미결 사항

- 스냅샷의 `order_qty` 유지 여부 (주문 변경 이력 추적 필요성 검토 중)
- `ship_need_date`에 스냅샷이 없을 때의 판단 기준 (현재 가정: 그 이전 가장 최근 스냅샷)
- `orders`와 `order_snapshots` 간 외래키 추가

스키마 주석은 한국어로 작성한다.

## Git workflow

- GitHub Flow: `main`은 항상 동작하는 상태로 유지하고, 모든 작업은 브랜치에서 한 뒤 PR로 머지한다.
- 브랜치 접두어: `feat/`, `fix/`, `docs/`, `chore/` + kebab-case (예: `feat/seed-fake-data`)
- 커밋 메시지: Conventional Commits + 한국어 설명 (예: `feat: 오더 및 일별 스냅샷 테이블 스키마 추가`)
- PR 설명에는 무엇 / 왜 / 어떻게 확인했는지를 적고, 관련 이슈는 `Closes #번호`로 연결한다.