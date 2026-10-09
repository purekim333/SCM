from dateutil.relativedelta import relativedelta

def month_range(start_date, end_date):
    '''
        끝 월 포함
        20260310과 20260520을 받으면
        20260301, 20260401, 20260501이 담긴 리스트를 반환
    '''
    month_list = []
    current_date = start_date.replace(day=1)
    while current_date <= end_date:
        month_list.append(current_date)
        current_date += relativedelta(months=1)

    return month_list
