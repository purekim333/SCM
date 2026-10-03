# SCM
I will be the best at SCM Programming!!

### 프로젝트 설명
이 프로젝트는 text2sql 설정을 하는 학습 페이지 입니다.
issue와 pr을 통해 매일을 기록하며 하루하루 성장해 나가고 있습니다.
저를 응원해주세요~!!

### 최초 실행 방법

```bash
cp .env.example .env

# .env 값 채우기

mysql -u <username> -p -e "CREATE DATABASE IF NOT EXISTS <db_name> CHARACTER SET utf8mb4;"

python -m venv venv

source venv/Scripts/activate

pip install -r requirements.txt

mysql -u <username> -p <db_name> < db/schema.sql

python script/seed_order_data.py
```

