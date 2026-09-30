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
    charset = 'utf8'
)


with connection:
    db = connection.cursor()
    with db :
        sql = "select 1 from dual "
        db.execute(sql)
        result = db.fetchall()
        print(result)

# 지정된 형태로 데이터 반복해서 집어넣기
# 데이터 형태는 key값은 order 연번이니까 increment하게
# 자재코드도 임의의 자릿수 숫자
# 흠 일단 스키마 보고 데이터 넣어야 하는데 이게 너무 빡이네