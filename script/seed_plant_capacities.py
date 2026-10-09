from date_utils import month_range
from dateutil.relativedelta import relativedelta

from db import get_connection

PLANT = "1120"
PLANT_DESC = "광주공장"
CAPA_QTY = 2000
CAPA_BUFFER_MONTHS = 6

sql = """
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
"""


def seed_plant_capacities():
    connection = get_connection()

    with connection:
        cursor = connection.cursor()
        cursor.execute("TRUNCATE TABLE plant_capacities")

        cursor.execute("select min(prod_need_date), max(prod_need_date) from orders")
        row = cursor.fetchone()
        min_prod_date, max_prod_date = row[0], row[1]

        for current_date in month_range(
            min_prod_date, max_prod_date + relativedelta(months=CAPA_BUFFER_MONTHS)
        ):
            cursor.execute(sql, (current_date, PLANT, PLANT_DESC, CAPA_QTY))

        connection.commit()


if __name__ == "__main__":
    seed_plant_capacities()
