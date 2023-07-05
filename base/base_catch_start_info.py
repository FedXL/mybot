import psycopg2
from psycopg2 import Error
from sheets.add_orders import add_last_string


async def start_add_user_to_base(user_id, user_first_name, user_second_name, user_name):
    from utils.config import user, host, port, database, password

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
        print("[INFO] check user in users")
        insert_1 = f"SELECT * FROM users WHERE user_id = {user_id};"
        cursor.execute(insert_1)
        user = cursor.fetchall()
        print('[INFO] user in base answer: ', user)
        if len(user) != 0:
            user = user[0]
            print("[INFO] Я понял что юзер есть.")
            if not user[3] or not user[4]:
                print('[INFO] Я понял что надо провести Update юзера нет фамилии или юзернейма')
                value = f"UPDATE users SET tele_username = '{user_name}'," \
                        f" user_second_name = '{user_second_name}'" \
                        f"WHERE user_id = '{user_id}';"
                cursor.execute(value)
            else:
                print("[INFO] catch_start я понял что поля у юзера есть и не надо ничего делать")

        else:
            print("[INFO] Я Понял что юзера нет и надо добавить его в БД")
            value2 = f"INSERT INTO users(user_id, user_name, tele_username ,user_second_name, is_kazakhstan)" \
                     f"VALUES ({user_id}, '{user_first_name}', '{user_name}', '{user_second_name}', '{True}');"
            cursor.execute(value2)

            await add_last_string([(user_id, user_first_name, user_name,user_second_name)], 'users_storage')

        connection.commit()

    except (Exception, Error) as error:
        print('[ERROR] ошибка в запросе к бд', error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("[INFO] Соединение с PostgreSQL закрыто")
