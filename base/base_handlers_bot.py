import psycopg2
from psycopg2 import Error
from sqlalchemy import insert
from sqlalchemy.orm import Session

from base.models import Posts
from utils.config import user, host, port, database, password, engine


def add_doc_to_bd(doc_id, user_id,message_id, is_answer=False, manager=None, ):
    if is_answer:
        preffix = f"🔸 [{manager}]: /doc_"
    else:
        preffix = "/doc_"
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
        print("[INFO] start executing add documents query")
        insert_1 = f"INSERT INTO messages (is_answer, storage_id,message_id) VALUES ({is_answer}, {user_id},{message_id}) RETURNING id;"
        cursor.execute(insert_1)
        id = cursor.fetchone()[0]
        print("[INFO] first success", id)

        insert_2 = f"INSERT INTO documents (document_id, message_id) VALUES ('{doc_id}', {id}) RETURNING id;"
        cursor.execute(insert_2)
        doc = preffix + f"{id}"
        print("[INFO] second success", "insert into documents ", id, doc_id)

        insert_3 = f"UPDATE messages SET message_body = '{doc}' WHERE id = {id};"
        cursor.execute(insert_3)
        print("[INFO] third success")
        connection.commit()

    except (Exception, Error) as error:
        print('[INFO] ошибка в запросе к бд', error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("[INFO] Соединение с PostgreSQL закрыто")


def add_photo_to_bd(photo_id, user_id,message_id, is_answer=False, manager=None):
    if is_answer:
        preffix = f"🔸 [{manager}]: /photo_"
    else:
        preffix = "/photo_"

    """photo_id это айдо фотографии в телеграмме
        user_id это айди пользователя в бд и в сообщении"""
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
        print("[INFO] start executing add photo query")
        insert_1 = f"INSERT INTO messages (is_answer,storage_id,message_id) VALUES ({is_answer}, {user_id},{message_id}) RETURNING id;"
        cursor.execute(insert_1)
        id = cursor.fetchone()[0]

        print('[INFO] first success', id, 'insert to messages', False, user_id)
        insert_2 = f"INSERT INTO photos (file_id, message_id) VALUES ('{photo_id}',{id});"
        cursor.execute(insert_2)
        print("[INFO] second success" "insert into photos", photo_id, id)
        photo = preffix + f"{id}"
        insert_3 = f"UPDATE messages SET message_body = '{photo}' WHERE id = {id};"
        cursor.execute(insert_3)
        print('[INFO] third success', 'insert to messages body', photo, 'where id = ', id)
        connection.commit()
    except (Exception, Error) as error:
        print('[INFO] ошибка в запросе к бд', error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("[INFO] Соединение с PostgreSQL закрыто")


def add_user_to_base(user_id, income, user_first_name=None, user_second_name=None, user_name=None):
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

    if income in ['KAZ_ORDER_LINKS', 'KAZ_ORDER_CABINET', 'PAYMENT']:
        is_kazakhstan = True
    else:
        is_kazakhstan = False

    print('[INFO] is in kazakhstan: ', is_kazakhstan)

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
                        f" user_second_name = '{user_second_name}'," \
                        f" is_kazakhstan = '{is_kazakhstan}'" \
                        f"WHERE user_id = '{user_id}';"
                cursor.execute(value)
            else:
                print("[INFO] Я понял что юзер есть имя фамилия заполнены остается только обновить is_kazakhstan")
                value = f"UPDATE users SET is_kazakhstan = '{is_kazakhstan}' WHERE user_id = {user_id};"
                cursor.execute(value)

        else:
            print("[INFO] Я Понял что юзера нет и надо добавить его в БД")
            value2 = f"INSERT INTO users(user_id, user_name, tele_username ,user_second_name, is_kazakhstan)" \
                     f"VALUES ({user_id}, '{user_first_name}', '{user_name}', '{user_second_name}', '{is_kazakhstan}');"
            cursor.execute(value2)
        connection.commit()

    except (Exception, Error) as error:
        print('[ERROR] ошибка в запросе к бд', error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("[INFO] Соединение с PostgreSQL закрыто")


def get_exchange():
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
        usd_insert = f"SELECT price,data FROM exchange WHERE valuta = 'usd';"
        cursor.execute(usd_insert)
        comeback = cursor.fetchone()
        usd, data = comeback
        eur_insert = f"SELECT price FROM exchange WHERE valuta = 'eur';"
        cursor.execute(eur_insert)
        eur = cursor.fetchone()[0]
    except (Exception, Error) as error:
        print('[INFO] ошибка в запросе к бд', error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print('$$$------> ', usd, eur, '<-------', sep="||")
            print("[INFO] Соединение с PostgreSQL закрыто")
            return (usd, eur, data)


def save_exhchange_to_bd(usd, eur, data):
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
        insert = f"UPDATE exchange SET price = {usd},data = '{data}' WHERE valuta = 'usd';" \
                 f"UPDATE exchange SET price = {eur},data = '{data}' WHERE valuta = 'eur';"
        cursor.execute(insert)
        connection.commit()
    except (Exception, Error) as error:
        print('[INFO] ошибка в запросе к бд', error)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("[INFO] Соединение с PostgreSQL закрыто , курсы валют обновлены")


def check_is_kazakhstan(user_id):
    """return true or false depents of ..."""
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
        print("[INFO] start executing add documents query")
        insert_1 = f"SELECT is_kazakhstan FROM users WHERE user_id = {user_id};"
        cursor.execute(insert_1)
        result = cursor.fetchone()[0]
        print("[INFO] first success", result)

    except (Exception, Error) as error:
        print('[INFO] ошибка в запросе к бд', error)
        result = error
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("[INFO] Соединение с PostgreSQL закрыто")
            return result


def add_post_to_base(message_id,chat_id,name):
    with Session(engine) as session:
        stmt = insert(Posts).values(message_id=message_id, chat_id=chat_id,name=name)
        session.execute(stmt)
        session.commit()
