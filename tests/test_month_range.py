from datetime import date
from date_utils import month_range
import pytest

# case 1 같은 해 안의 기간 (20260304 ~ 20260701)
def test_month_range_same_year():
    result = month_range(date(2026,3,4), date(2026,7,1))
    expected = [date(2026,3,1), date(2026,4,1), date(2026,5,1), date(2026,6,1), date(2026,7,1)]
    assert  result == expected

# case 2 연도를 넘어가는 기간 (20261001 ~ 20270301)
def test_month_range_different_year():
    result = month_range(date(2026,10,1), date(2027,3,1))
    expected = [date(2026,10,1), date(2026,11,1), date(2026,12,1), date(2027,1,1), date(2027,2,1), date(2027,3,1)]
    assert result == expected

# case 3 시작월과 끝월이 같은 기간 (20261003, 20261023)
def test_month_range_same_month():
    result = month_range(date(2026,10,3), date(2026,10,23))
    expected = [date(2026,10,1)]
    assert result == expected

# case 4 완전 같은 기간 (20261009, 20261009)
def test_month_range_same_date():
    result = month_range(date(2026,10,9), date(2026,10,9))
    expected = [date(2026,10,1)]
    assert result == expected

# case 5 기간 설정 오류 (20261009, 20261008)
def test_month_range_wrong_date():
    with pytest.raises(ValueError):
        month_range(date(2026,10,9), date(2026,10,8))
