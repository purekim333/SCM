# SCM Agent

> 제조 공급망 데이터를 스스로 조회하고 해석하는 AI 에이전트를, 프레임워크 없이 바닥부터 만들어 갑니다.
> I will be the best at SCM Programming!!

## 무엇을 만드나

"이번 달 지연된 미국향 오더는? 왜 늦었어?" 같은 질문에 답하는 에이전트입니다.

```
질문 → DB 구조 파악 → SQL 생성·실행 → (필요하면) 웹 검색 → 인사이트 있는 답변
```

문서를 검색하는 RAG 챗봇과 달리, **실제 오더 데이터를 직접 조회**해서 답합니다.

## 원칙

- **프레임워크 없이**: LangChain 같은 도구 없이 Anthropic SDK의 tool use만으로 에이전트 루프를 직접 구현합니다.
- **약속과 사실의 분리**: 오더(약속)와 일별 스냅샷(사실)을 다른 테이블에 담고, 판단은 계산으로 꺼냅니다.
- **가짜 데이터만**: 실제 회사 데이터는 사용하지 않습니다.

## 기술 스택

Python · MySQL 8 · PyMySQL · Anthropic SDK

## 데이터 모델

| 테이블 | 설명 |
|---|---|
| `orders` | 오더 라인당 한 행. 납품요청일 ← 선적필요일 ← 생산필요일을 리드타임으로 역산 |
| `order_snapshots` | 매일의 생산·적입·출하 상태를 그대로 쌓음 |

**지연 기준**: 선적필요일 시점에 `ship_qty < order_qty`이면 지연.

## 폴더 구조

```
├── db/
│   ├── schema.sql          # 테이블 생성 (재실행 시 데이터 삭제됨)
│   └── verify_orders.sql   # 시드 데이터 검증 쿼리
├── script/
│   └── seed_order_data.py  # 가짜 오더 생성
├── docs/
│   └── PROGRESS.md         # 진행 상황과 학습 로그
└── CLAUDE.md               # 프로젝트 규칙과 도메인 정의
```

## 시작하기

> Windows + Git Bash 기준입니다. 필요한 것: Python 3.12+, MySQL 8.

**1. 환경 변수**
```bash
cp .env.example .env   # DB 접속 정보와 API 키를 채운다
```

**2. 가상환경과 패키지**
```bash
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
```

**3. 데이터베이스와 테이블**
```bash
mysql -u <username> -p -e "CREATE DATABASE IF NOT EXISTS <db_name> CHARACTER SET utf8mb4;"
mysql -u <username> -p <db_name> < db/schema.sql
```

**4. 가짜 데이터 넣고 검증하기**
```bash
python script/seed_order_data.py
mysql -u <username> -p --default-character-set=utf8mb4 <db_name> < db/verify_orders.sql
```
검증 쿼리는 규칙을 어긴 행만 보여줍니다. 출력이 없으면 통과입니다.

## 로드맵

- [x] 오더 가짜 데이터 생성과 검증
- [ ] 일별 스냅샷 시뮬레이션, 지연 조회 뷰
- [ ] SQL 실행 도구와 에이전트 루프
- [ ] 평가 세트와 안전장치 (SELECT only, LIMIT)
- [ ] 웹 검색, 인사이트 답변, 데모

진행 상황과 매일의 학습 기록은 [docs/PROGRESS.md](docs/PROGRESS.md)에 있습니다. 이슈와 PR로 매일 성장하고 있어요. 응원해 주세요! 🙌