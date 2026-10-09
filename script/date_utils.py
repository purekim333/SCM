from datetime import timedelta

from dateutil.relativedelta import relativedelta


def month_range(start_date, end_date):
    """
    끝 월 포함
    20260310과 20260520을 받으면
    20260301, 20260401, 20260501이 담긴 리스트를 반환

    끝 월이 시작월보다 작으면 ValueError
    """

    if start_date > end_date:
        raise ValueError("입력기간 오류: 끝 월이 시작월보다 작을 수 없습니다.")

    month_list = []
    current_date = start_date.replace(day=1)
    while current_date <= end_date:
        month_list.append(current_date)
        current_date += relativedelta(months=1)

    return month_list


LOCK_DATE_STANDARD = 5


def plan_lock_date(input_date):
    """
    년, 월을 입력받으면 해당 말일에서 5일 앞의 생산반영일을 반환
    다음 달 계획을 확정하는 날
    다음달로 더한 뒤에 5일 감소
    """
    last_month_date = input_date.replace(day=1) + relativedelta(day=31)

    cnt = 0
    current_date = last_month_date

    while True:
        print("현재 날짜:", current_date, current_date.weekday())

        # 현재 날짜가 평일이라면
        if current_date.weekday() < 5:
            cnt += 1
            if cnt == LOCK_DATE_STANDARD:
                return current_date

        current_date -= timedelta(days=1)
