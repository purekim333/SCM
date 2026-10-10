DROP TABLE IF EXISTS component_receipts;
DROP TABLE IF EXISTS bom_items;
DROP TABLE IF EXISTS plant_capacities;
DROP TABLE IF EXISTS supply_plans;
DROP VIEW IF EXISTS vw_order_delay;
DROP VIEW IF EXISTS vw_order_progress;
DROP TABLE IF EXISTS order_snapshots;
DROP TABLE IF EXISTS orders;


CREATE TABLE orders(
  -- 오더 번호
  sales_order varchar(20),
  sales_order_item varchar(20),

  -- 어느공장에서 생산할것인지
  plant varchar(20),
  plant_desc varchar(20),

  -- 납품처 번호
  shipto varchar(20),

  -- 자재 코드
  mtrl_code varchar(20),
  mtrl_desc varchar(20),
  
  -- 주문수량
  order_qty INT,

  -- 주문 받은 날짜

  order_date DATE,

  -- 납품요청일 (이날까지 가져다 주세요)
  rqst_date DATE,

  -- 선적필요일 리드타임을 고려해서 이날까지 선적이 되어야만 함 (미국은 3개월씩 걸림)
  ship_need_date DATE,

  -- 생산필요일 (이날까지 가져다 주려면 이날까지 생산이 다 되어야만 함)
  prod_need_date DATE,

  primary key (sales_order, sales_order_item)
);

-- 오더 스냅샷에서 오늘 order qty와 ship_qty를 비교해봐야 한다
-- 만약 order qty = ship qty가 같아진다 이때 모두 출하가 되었다는 뜻
-- 선적필요일 날짜의 스냅샷에서 ship_qty가 order_qty보다 작으면 지연

CREATE TABLE order_snapshots(
  -- 오더 번호
  sales_order varchar(20),
  sales_order_item varchar(20),

  -- 오더 스냅샷 일자
  cut_off_date DATE,

  -- 이날짜의 해당 오더의 상태는
  order_qty INT, -- 총 주문 수량
  prod_qty INT, -- 생산 수량
  carry_over_qty INT, -- 이월 수량
  stuffing_qty INT, -- 적입 수량
  ship_qty INT, -- 출하 수량 (누적)

  primary key (sales_order, sales_order_item, cut_off_date)
  
);

CREATE TABLE supply_plans(
  sales_order varchar(20),
  sales_order_item varchar(20),
  plan_month DATE, -- 계획 월 (매월 1일로 저장)
  order_qty INT, -- 오더 수량 (반정규화)
  demand_qty INT, -- 수요 수량 (이번달에 들어가야 하는 양)
  prod_qty INT, -- 생산반영 수량
  carry_over_qty INT, -- 생산 미반영 수량
  short_reason varchar(20), -- 생산 미반영 이유 (CAPA, MATERIAL, NULL)

  PRIMARY KEY (plan_month, sales_order, sales_order_item)
);


CREATE TABLE plant_capacities(
  plan_month DATE, -- 공장 월별 캐파 계산을 위한 플랜 월
  plant varchar(20), -- 공장 코드
  plant_desc varchar(20), -- 공장 이름
  capa_qty INT, -- 월 생산 가능 수량(대)

  PRIMARY KEY (plan_month, plant)
);

-- bom 테이블 완제품 하나에 component_code 하나씩 여러 행이 나오는 구조
CREATE TABLE bom_items(
  mtrl_code varchar(20), -- 완제품 코드
  mtrl_desc varchar(20), -- 완제품 이름

  component_code varchar(20), -- 부품 코드
  component_desc varchar(20), -- 부품 이름
  component_qty_per_unit INT, -- 완제품 1대당 부품 수량

  PRIMARY KEY (mtrl_code, component_code)
);

-- 부품 입고 (Goods Receipt). 입고 문서(gr_no) 하나에 아이템(gr_item) 여러 줄
-- 헤더 정보(입고일, 공장, 협력사)는 orders처럼 아이템마다 반복해서 담는다
CREATE TABLE component_receipts(
  gr_no varchar(20),          -- 입고 문서 번호
  gr_item varchar(20),        -- 입고 문서 아이템 번호

  receipt_date DATE,          -- 입고일 (전기일)
  plant varchar(20),          -- 입고 공장 코드
  plant_desc varchar(20),     -- 입고 공장 이름
  vendor varchar(20),         -- 협력사 코드
  vendor_desc varchar(40),    -- 협력사 이름

  po_no varchar(20),          -- 구매 오더 번호 (어떤 발주에 대한 입고인지)
  po_item varchar(20),        -- 구매 오더 아이템 번호

  component_code varchar(20), -- 부품 코드
  component_desc varchar(20), -- 부품 이름
  receipt_qty INT,            -- 입고 수량

  PRIMARY KEY (gr_no, gr_item)
);
