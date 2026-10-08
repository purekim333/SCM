import os
from dotenv import load_dotenv

import pymysql
from dateutil.relativedelta import relativedelta
from db import get_connection

connection = get_connection()

PLANT = '1120'
PLANT_DESC = '광주공장'
CAPA_QTY = 2000
CAPA_BUFFER_MONTHS = 6

sql = '''
INSERT INTO plant_capacities (
    plan_month,
    plant, plant_desc,
    capa_qty
)
VALUES (
    %s,
    %s, %s,
    %s
)
'''

with connection:
    cursor = connection.cursor()
    cursor.execute("TRUNCATE TABLE plant_capacities")
    print("DB 초기화")

    cursor.execute("select min(prod_need_date), max(prod_need_date) from orders")
    row = cursor.fetchone()
    first_month, last_month = row[0].replace(day=1), row[1].replace(day=1)
    print(first_month)
    print(last_month)


    current_month = first_month
    while current_month <= last_month + relativedelta(months=CAPA_BUFFER_MONTHS):
        print("현재 Insert 날짜: ", current_month)
        cursor.execute(sql, (current_month, PLANT, PLANT_DESC, CAPA_QTY))
        current_month += relativedelta(months=1)

    connection.commit()