from datetime import date

import pytest
from date_utils import plan_lock_date


@pytest.mark.parametrize(
    ("input_date", "expected"),
    [
        (date(2026, 1, 1), date(2026, 1, 26)),
        (date(2026, 2, 14), date(2026, 2, 23)),
        (date(2026, 5, 22), date(2026, 5, 25)),
        (date(2026, 9, 22), date(2026, 9, 24)),
        (date(2026, 4, 22), date(2026, 4, 24)),
    ],
)
def test_plan_lock_date(input_date, expected):
    assert plan_lock_date(input_date) == expected
