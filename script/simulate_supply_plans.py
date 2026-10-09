import pymysql
from date_utils import month_range, plan_lock_date
from dateutil.relativedelta import relativedelta

from db import get_connection

DEMAND_SQL = """
    (
    select 2 as priority
        , sales_order
        , sales_order_item
        , order_qty
        , order_qty as demand_qty
        , prod_need_date
    from orders o
    where prod_need_date < %s
        and order_date <= %s
        and not EXISTS
        (select 1
            from supply_plans sp
            where o.sales_order = sp.sales_order
            and o.sales_order_item = sp.sales_order_item
        )
    )
    UNION ALL
    (
    select 1 as priority 
        , sp.sales_order
        , sp.sales_order_item
        , sp.order_qty
        , sp.carry_over_qty as demand_qty
        , o.prod_need_date
    from supply_plans sp
    join orders o
    on sp.sales_order = o.sales_order
        and sp.sales_order_item = o.sales_order_item
    where plan_month = %s
        and carry_over_qty > 0
    )
    order by priority, prod_need_date, sales_order, sales_order_item
"""

CAPA_SQL = """
    SELECT capa_qty FROM plant_capacities
    where plan_month = %s
"""

INSERT_SQL = """
    INSERT INTO supply_plans(
        sales_order, sales_order_item,
        plan_month,
        order_qty, demand_qty,
        prod_qty, carry_over_qty, short_reason
    ) VALUES (
        %s, %s,
        %s,
        %s, %s,
        %s, %s, %s
    )
"""


def plan_one_month(capa, demands):
    """
    정렬된 demands를 입력으로 받음 (이월분 먼저, prod_need_date 순)
    앞에서부터 캐파를 배분, 모자라면 반영하고 나머지는 이월 + 'CAPA'
    """
    remain_capa = capa
    result = []

    for demand in demands:
        prod_qty = min(remain_capa, demand["demand_qty"])
        carry_over_qty = demand["demand_qty"] - prod_qty
        short_reason = None
        if carry_over_qty > 0:
            short_reason = "CAPA"
        result.append(
            {
                **demand,
                "prod_qty": prod_qty,
                "carry_over_qty": carry_over_qty,
                "short_reason": short_reason,
            }
        )
        remain_capa -= prod_qty

    return result


def simulate_supply_plans():
    # 1. supply_plans 비우기 (멱등: 몇 번 돌려도 같은 결과)
    # 2. 시뮬레이션할 월 목록 구하기 (month_range)
    # 3. 월마다:
    #    3-1. 반영일 구하기: 이 달 계획은 "전월"의 반영일에 확정 (2월 계획 → 1/26)
    #    3-2. 이번 달 캐파 읽기 (plant_capacities)
    #    3-3. 수요 읽기 = 전월 이월분 + 이번 달 신규 오더 (정렬해서)
    #    3-4. plan_one_month(캐파, 수요)
    #    3-5. 결과에 plan_month 붙여서 INSERT
    # 4. commit
    connection = get_connection()

    with connection:
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("TRUNCATE TABLE supply_plans")

        cursor.execute(
            "select min(prod_need_date) as min_prod_need_date, max(prod_need_date) as max_prod_need_date from orders"
        )
        record = cursor.fetchone()

        min_prod_need_date, max_prod_need_date = (
            record["min_prod_need_date"],
            record["max_prod_need_date"],
        )
        plan_month_list = month_range(min_prod_need_date, max_prod_need_date)

        for plan_month in plan_month_list:
            next_month = plan_month + relativedelta(months=1)
            prev_month = plan_month - relativedelta(months=1)

            lock_date = plan_lock_date(prev_month)
            prev_plan_month = prev_month

            cursor.execute(DEMAND_SQL, (next_month, lock_date, prev_plan_month))
            demand_record = cursor.fetchall()

            cursor.execute(CAPA_SQL, (plan_month,))
            capa_record = cursor.fetchone()["capa_qty"]

            result_list = plan_one_month(capa_record, demand_record)

            for result in result_list:
                cursor.execute(
                    INSERT_SQL,
                    (
                        result["sales_order"],
                        result["sales_order_item"],
                        plan_month,
                        result["order_qty"],
                        result["demand_qty"],
                        result["prod_qty"],
                        result["carry_over_qty"],
                        result["short_reason"],
                    ),
                )
        connection.commit()


if __name__ == "__main__":
    simulate_supply_plans()
