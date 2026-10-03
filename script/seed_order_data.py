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
    host = db_host,
    port = db_port,
    user = db_username,
    password = db_password,
    database = db_name,
    charset = 'utf8mb4'
)

sql =""" 
INSERT INTO 
orders (
    SALES_ORDER, SALES_ORDER_ITEM,
    PLANT, PLANT_DESC,
    SHIPTO,
    MTRL_CODE, MTRL_DESC,
    ORDER_QTY,
    RQST_DATE, SHIP_NEED_DATE, PROD_NEED_DATE
)
VALUES(
    %s, %s,
    %s, %s,
    %s,
    %s, %s,
    %s,
    %s, %s, %s
) 
"""

# 오더 예시
# value_list = [
#     ("S00100", "10", 
#      "1120", "광주공장",
#      "1004447",
#      "234553", "전기자전거01",
#      200,
#      "20261231", "20261201", "20261101" 
#      ),
# ]

# 주문번호 생성
order_list = range(100, 140)

# 랜덤 날짜 생성
random.seed(42) # 랜덤 시드 고정(재현성)

# 정해진 규칙은 그럼 25년 이후 중 임의의 날짜를 납품요청일로 설정하고
# 해당 날짜를 기준으로 생산 리드타임, 물류 리드타임 고려 하는 걸로
# 임의의 리드타임 지금 설정

start_date_range = datetime(2025, 1, 1)
prod_lt = timedelta(days=30)
ship_lt = timedelta(days=60)

with connection:
    db = connection.cursor()
    with db :
        db.execute(("TRUNCATE TABLE orders"))

        for order in order_list:

            item_cnt = random.randint(1,10)

            rqst_date = start_date_range + timedelta(days=random.randint(1,1095))
            ship_need_date = rqst_date - ship_lt
            prod_need_date = ship_need_date - prod_lt

            for item in range(1, item_cnt+1):

                so = f"S{order:05}"
                so_item = str(item * 10)

                record = (so, so_item, '1120', '광주공장', '1004447', '234555',
                          '전기자전거', 200, rqst_date, ship_need_date, prod_need_date)
                
                db.execute(sql, record)

        connection.commit()
        db.execute(("select count(*) from orders"))
        print("db 실행결과: ", db.fetchone())
