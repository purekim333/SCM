-- 오더 검증
-- 과거 현재 미래 데이터 갯수 검증
-- 기대결과: 과거, 현재, 미래 별 건수 확인
SELECT 
  CASE
    WHEN
      rqst_date < CURRENT_DATE
    THEN '과거'
    WHEN
      rqst_date = CURRENT_DATE
    THEN '현재'
    WHEN
      rqst_date > CURRENT_DATE
    THEN '미래'
  END AS order_status
  , count(DISTINCT sales_order) as 'cnt_sales_order'
FROM
  orders
GROUP BY
  order_status
;

-- 오더별 서로 다른 rqst_date 존재 여부 검증
-- 예상결과 : 0행 (출력없음)
SELECT 
  sales_order, count(*), count(distinct rqst_date) AS 'cnt_rqst_date'
FROM orders
GROUP BY sales_order
HAVING cnt_rqst_date > 1
;

-- 날짜 순서 검증 (rqst date > ship_need_date > prod_need_date)
-- 예상결과 : 0행 (출력없음)
SELECT sales_order
FROM orders
WHERE 
  rqst_date <= ship_need_date
  OR
  ship_need_date <= prod_need_date
;

-- 긴급오더 범위 10퍼센트 확인
-- 예상결과: 정상오더: 퍼센트, 긴급오더: 퍼센트

SELECT 
  CASE WHEN
    DATEDIFF(rqst_date, order_date) < 130
  THEN '긴급'
  WHEN
    DATEDIFF(rqst_date, order_date) >= 130
  THEN '정상'
  END AS order_type,
  count(distinct sales_order) as order_cnt,
  count(distinct sales_order) / sum(count(distinct sales_order)) over() as ratio 
FROM orders
GROUP BY order_type

