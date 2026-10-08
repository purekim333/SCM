import os
from dotenv import load_dotenv
import pymysql

def get_connection():
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
    return connection