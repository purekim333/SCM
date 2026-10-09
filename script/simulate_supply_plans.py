SQL = """
    INSERT INTO SUPPLY_PLANS(
        sales_order, sales_order_item,
        plan_month,
        order_qty,
        demand_qty,
        prod_qty, carry_over_qty, short_reason
    )
    VALUES(
        %s, %s,
        %s,
        %s,
        %s,
        %s, %s, %s
    )
"""


def plan_one_month(capa, demands):
    '''
    정렬된 demands를 입력으로 받음 (이월분 먼저, prod_need_date 순)
    앞에서부터 캐파를 배분, 모자라면 반영하고 나머지는 이월 + 'CAPA'
    '''
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
    pass


if __name__ == "__main__":
    simulate_supply_plans()
