import psycopg2
from psycopg2 import Error
from utils.config import user, host, port, database, password


def get_orders_info():
    try:
        connection = psycopg2.connect(user=user,
                                  password=password,
                                  host=host,
                                  port=port,
                                  database=database)

        cursor = connection.cursor()
    except (Exception, Error) as error:
        print("[INFO] Ошибка при работе с PostgreSQL", error)
        return
    try:
        # usd_insert = f"SELECT * FROM orders;"
        query = "SELECT client,id,to_char(time, 'YYYY-MM-DD HH24:MI:SS') as time,buyer,type,body  FROM orders;"
        cursor.execute(query)

        cursor.execute(query)
        comeback = cursor.fetchall()
        result = comeback

    except (Exception, Error) as error:
        print('[INFO] ошибка в запросе к бд', error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            return (result)


def get_users_info():
    try:
        connection = psycopg2.connect(user=user,
                                  password=password,
                                  host=host,
                                  port=port,
                                  database=database)

        cursor = connection.cursor()
    except (Exception, Error) as error:
        print("[INFO] Ошибка при работе с PostgreSQL", error)
        return
    try:
        # usd_insert = f"SELECT * FROM orders;"
        query = "SELECT user_id,user_name,user_second_name,tele_username FROM users;"
        cursor.execute(query)

        cursor.execute(query)
        comeback = cursor.fetchall()
        result = comeback

    except (Exception, Error) as error:
        print('[INFO] ошибка в запросе к бд', error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            return (result)