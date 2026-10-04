import os
from dotenv import load_dotenv
import pymysql 
import random
from datetime import datetime, timedelta

# 환경 변수 불러오기
load_dotenv()

db_host = os.getenv("DB_HOST")
db_port = int(os.getenv("DB_PORT"))
db_name = os.getenv("DB_NAME")
db_username = os.getenv("DB_USERNAME")
db_password = os.getenv("DB_PASSWORD")

# 로컬 mysql이랑 연결하기
connection = pymysql.connect(
    host=db_host,
    port=db_port,
    user=db_username,
    password=db_password,
    database=db_name,
    charset='utf8mb4'
)

sql =""" 
INSERT INTO 
orders (
    SALES_ORDER, SALES_ORDER_ITEM,
    PLANT, PLANT_DESC,
    SHIPTO,
    MTRL_CODE, MTRL_DESC,
    ORDER_QTY, ORDER_DATE,
    RQST_DATE, SHIP_NEED_DATE, PROD_NEED_DATE
)
VALUES(
    %s, %s,
    %s, %s,
    %s,
    %s, %s,
    %s, %s,
    %s, %s, %s
) 
"""

ORDER_CNT = 40
RQST_DATE_RANGE = 1095
PROD_LT_DAYS = 30
SHIP_LT_DAYS = 60

## 긴급오더 판단
URGENT_ORDER_RATIO = 0.1 #10퍼센트 정도 눈치없는 오더라고 가정

## 수주 간격 범위
COMMON_ORDER_DAYS = 130
URGENT_ORDER_MIN_DAYS = 95
COMMON_ORDER_MAX_DAYS = 200


# 주문번호 생성
order_list = range(100, 100 + ORDER_CNT)

# 랜덤 날짜 생성
random.seed(42) # 랜덤 시드 고정(재현성)
start_date_range = datetime(2025, 1, 1)

# 리드 타임 설정
prod_lt = timedelta(days=PROD_LT_DAYS)
ship_lt = timedelta(days=SHIP_LT_DAYS)

with connection:
    cursor = connection.cursor()
    with cursor:
        cursor.execute(("TRUNCATE TABLE orders"))

        for order in order_list:

            item_cnt = random.randint(1,10)

            rqst_date = start_date_range + timedelta(days=random.randint(1,RQST_DATE_RANGE))
            ship_need_date = rqst_date - ship_lt
            prod_need_date = ship_need_date - prod_lt

            if random.random() < URGENT_ORDER_RATIO: #10퍼센트 확률로 긴급오더
                order_date = rqst_date - timedelta(days=random.randint(URGENT_ORDER_MIN_DAYS, COMMON_ORDER_DAYS-1))
            else:
                order_date = rqst_date - timedelta(days=random.randint(COMMON_ORDER_DAYS, COMMON_ORDER_MAX_DAYS))

            for item in range(1, item_cnt+1):
                so = f"S{order:05}"
                so_item = str(item * 10)

                record = (so, so_item, '1120', '광주공장', '1004447', '234555',
                          '전기자전거', 200, order_date, rqst_date, ship_need_date, prod_need_date)
                
                cursor.execute(sql, record)

        connection.commit()
        cursor.execute(("select count(*) from orders"))
        print("db 실행결과: ", cursor.fetchone())
