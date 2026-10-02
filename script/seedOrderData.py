import os
from dotenv import load_dotenv
import pymysql 

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

# value_list = [
#     ("S00100", "10", 
#      "1120", "광주공장",
#      "1004447",
#      "234553", "전기자전거01",
#      200,
#      "20261231", "20261201", "20261101" 
#      ),
#     ("S00100", "20", 
#      "1120", "광주공장",
#      "1004447",
#      "234563", "전기자전거02",
#      120,
#      "20261231", "20261201", "20261101"   
#      )
# ]

order_list = range(100, 110)
order_item_list = range(10, 10*10+1, 10)

with connection:
    db = connection.cursor()
    with db :
        db.execute(("TRUNCATE TABLE orders"))

        for order in order_list:
            for order_item in order_item_list:
                so = f"S{order:05}"
                so_item = order_item

                record = (so, so_item, '1120', '광주공장', '1004447', '234555',
                          '전기자전거', 200, '20261231', '20261201', '20261101')
                
                db.execute(sql, record)

        connection.commit()
        db.execute(("select count(*) from orders"))
        print("db 실행결과: ", db.fetchone())
