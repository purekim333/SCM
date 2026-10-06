-- 월별 수요합계 조회
SELECT 
    DATE_FORMAT(prod_need_date, '%Y-%m') as prod_month
    , sum(order_qty) as monthly_demand_qty
FROM
    orders
GROUP BY prod_month
ORDER BY prod_month