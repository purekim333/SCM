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
