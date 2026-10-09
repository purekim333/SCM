from simulate_supply_plans import plan_one_month


def test_plan_one_month_carries_over_when_capa_short():
    result = plan_one_month(
        1000,
        [
            {
                "sales_order": "S00100",
                "sales_order_item": "10",
                "order_qty": 1200,
                "demand_qty": 400,
            },
            {
                "sales_order": "S00101",
                "sales_order_item": "10",
                "order_qty": 500,
                "demand_qty": 500,
            },
            {
                "sales_order": "S00101",
                "sales_order_item": "20",
                "order_qty": 300,
                "demand_qty": 300,
            },
        ],
    )
    expected = [
        {
            "sales_order": "S00100",
            "sales_order_item": "10",
            "order_qty": 1200,
            "demand_qty": 400,
            "prod_qty": 400,
            "carry_over_qty": 0,
            "short_reason": None,
        },
        {
            "sales_order": "S00101",
            "sales_order_item": "10",
            "order_qty": 500,
            "demand_qty": 500,
            "prod_qty": 500,
            "carry_over_qty": 0,
            "short_reason": None,
        },
        {
            "sales_order": "S00101",
            "sales_order_item": "20",
            "order_qty": 300,
            "demand_qty": 300,
            "prod_qty": 100,
            "carry_over_qty": 200,
            "short_reason": "CAPA",
        },
    ]
    assert result == expected


### 2 경계값 테스트
def test_plan_one_month_same_capa_and_demand_qty():
    result = plan_one_month(
        400,
        [
            {
                "sales_order": "S00100",
                "sales_order_item": "10",
                "order_qty": 1200,
                "demand_qty": 400,
            }
        ],
    )
    expected = [
        {
            "sales_order": "S00100",
            "sales_order_item": "10",
            "order_qty": 1200,
            "demand_qty": 400,
            "prod_qty": 400,
            "carry_over_qty": 0,
            "short_reason": None,
        }
    ]
    assert result == expected
