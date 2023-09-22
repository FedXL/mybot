import re
import aiogram.utils.markdown as md
from aiogram import types
from aiogram.types import CallbackQuery, Message
from base.base_connectors import get_from_base
from utils.utils_lite import create_counter

def make_no_discount_text(money):
    text = md.text(
        md.text('<b>Накопительные скидки при оплате на сайте Tradeinn</b>'),
        md.text(' '),
        md.text('Мы рады, что вы с нами и заказываете товары на Tradeinn.com с нашей помощью.'),
        md.text(' '),
        md.text('Комиссия по оплате будет зависеть от суммы всех ваших заказов, включая текущий:'),
        md.text(' '),
        md.text('🔹 до 100k - 10%'),
        md.text('🔹 от 100к до 200k - 8%'),
        md.text('🔹 от 200к - 7%'),
        md.text(' '),
        md.text(f'Вы заказали товаров на сумму {money} тыс.руб. Ваша комиссия пока 10%, но это легко поправить!'),
        md.text(' '),
        md.text('<b>ДО 1 АВГУСТА ВЫ МОЖЕТЕ СДЕЛАТЬ ЗАКАЗЫ С КОМИССИЕЙ 8%!</b>'),sep='\n')
    return text

def make_discount_text(discount):
    text = md.text(
        md.text('<b>Накопительные скидки при оплате на сайте Tradeinn</b>'),
        md.text(' '),
        md.text('Мы рады, что вы с нами и заказываете товары на Tradeinn.com с нашей помощью.'),
        md.text(' '),
        md.text('Комиссия по оплате будет зависеть от суммы всех ваших заказов, включая текущий:'),
        md.text(' '),
        md.text('🔹 до 100k - 10%'),
        md.text('🔹 от 100к до 200k - 8%'),
        md.text('🔹 от 200к - 7%'),
        md.text(' '),
        md.text(f'<b>ВАША КОМИССИЯ ПРИ ОПЛАТЕ - {discount}%</b>'), sep='\n')
    return text








def make_text_hello(username):
    text_hello = md.text(
        md.text("🫱   Добро пожаловать,", "*", username, "*", "!", "Я Бот-Помощник."),
        md.text(" "),
        md.text("🔸  Могу оформить заказ , в разделе 'Сделать заказ'."),
        md.text(""),
        md.text("🔸  Ответы на большинство вопросов и калькулятор стоимости в разделе 'Kонсультация'."),
        md.text(" "),
        md.text(
            "🗣  В случае необходимости, и, если раздел консультаций не помог, для связи с живым консультантом просто пишите в чат. "),
        sep="\n"
    )
    return text_hello


def thank_u():
    text = md.text(
        md.text("🔶 Благодарим за заказ! 🔶"),
        md.text(" "),
        md.text("Будем рады дальнейшему сотрудничеству."
                " Если вам понравился наш сервис, оставьте отзыв в канале"
                " https://t.me/shipkz_discussing."),
        md.text(" "),
        sep="\n",
    )
    return text


def make_text_for_FAQ(value: str):
    try:
        with open("storages" + value + ".html", "r", ) as fi:
            result = fi.read()
            fi.close()
    except Exception as ex:
        print("чето пошло не так")
    return result


def make_user_info_report(query: CallbackQuery, order_id=None) -> md.text():
    user_id = query.from_user.id
    user_first_name = query.from_user.first_name
    user_second_name = query.from_user.last_name
    username = query.from_user.username
    result = md.text(
        md.text(f" #{order_id}"),
        md.text(f"Type: <b>{query.data}</b>"),
        md.text(f"User: ", md.hlink(f"#ID_{user_id}", f"tg://user?id={user_id}")),
        md.text(f"First Name: {user_first_name}"),
        md.text(f"Second Name: {user_second_name}"),
        md.text(f"UserName :  @{username}"),
        sep="\n"
    )
    return result


def make_user_info_report_from_message(message: types.Message):
    user_id = message.from_user.id
    user_first_name = message.from_user.first_name
    user_second_name = message.from_user.last_name
    result = md.text(
        md.text(f"#ID_{user_id}"),
        md.text(f"First Name: {user_first_name}"),
        f"|",
        md.text(f"Second Name: {user_second_name}"),
        sep="\n"
    )
    return result


def add_orders_to_mask(id, mask:list) ->list:
    """добавляет в маску активные ордера если они есть"""
    stmt = f"""SELECT order_status.order_id, order_status.manager_id FROM orders 
                JOIN order_status ON orders.id = order_status.order_id
                WHERE order_status.status = true
                AND orders.client = {id}
                ORDER BY order_status.order_id DESC;"""

    query_set = get_from_base(stmt)
    if query_set:
        for order in query_set:
            order_str = "/order_" + str(order[0])
            manager_str = str([order[1]]).replace("'", "")
            if manager_str != '[None]':
                order_id = order[0]

                stmt2 = f"""SELECT managers.short_name FROM order_status
                                JOIN managers ON order_status.manager_id = managers.user_id
                                WHERE order_status.order_id = {order_id}"""

                short_name = get_from_base(stmt2)[0][0]
                manager_str = "[" + str(short_name) + "]"
            mask.append(order_str + " | " + manager_str)
    return mask


def get_mask_from_message(text_to_parce):
    """ маска со стороны менеджеров """
    result = []
    id = get_id_from_text(text_to_parce)
    text_to_parce = text_to_parce.split("\n")

    result.append(f"#ID_{id}")
    result.append(text_to_parce[1])

    result = add_orders_to_mask(id, result)
    return result

def get_mask_from_web_message(text_to_parce,user_id):
    result = []
    text_to_parce = text_to_parce.split("\n")
    result.append(f"#WEB_{user_id}")
    result.append(text_to_parce[1])
    return result

def make_mask_to_messages(income, user_id):
    """это делает маску со стороны юзеров"""
    assert isinstance(income, types.Message) or isinstance(income, types.CallbackQuery)
    user_first_name = income.from_user.first_name
    user_second_name = income.from_user.last_name
    result = [
        md.text(f"#ID_{user_id}"),
        md.text(f"{user_first_name}",
                f"|",
                f"{user_second_name}",
                )]
    result = add_orders_to_mask(user_id, result)
    result = md.text(*result,sep="\n")
    return result


def order_answer_vocabulary(income, order_id):
    match income:
        case 'KAZ_ORDER_LINKS':
            text = ['Вариант 1', f'Заказ через Казахстан №{order_id}', 'ссылки']
        case 'KAZ_ORDER_CABINET':
            text = ['Вариант 1', f'Заказ через Казахстан №{order_id}', 'доступ в кабинет']
        case 'TRADEINN':
            text = ['Вариант 2', f'Заказ через TradeInn №{order_id}']
        case 'PAYMENT':
            text = ['Вариант 3', f'Выкуп через посредника №{order_id}']
    return text


def make_links_info_text(links):
    counter = create_counter()
    md_obj = [md.hlink("ссылка " + str(counter()), link) for link in links]
    return md_obj


def get_vaflalist(pos=1):
    if pos == 1:
        result = ('первая',
                  'вторая',
                  'третья',
                  'четвертая',
                  'пятая',
                  'шестая',
                  'седьмая',
                  'восьмая',
                  'девятая',
                  'десятая',
                  'одиннадцатая',
                  'двенадцатая',
                  'тринадцатая',
                  'четырнадцатая',
                  'пятнадцатая')
    elif pos == 2:
        result = ('первой',
                  'второй',
                  'третьей',
                  'четвертой',
                  'пятой',
                  'шестой',
                  'седьмой',
                  'восьмой',
                  'девятой',
                  'десятой',
                  'одиннадцатой',
                  'двенадцатой',
                  'тринадцатой',
                  'четырнадцатой',
                  'пятнадцатой',)
    return result


def get_additional_from_proxi(data):
    """Не помню уже видимо что то связанное с созданием текста в ордере"""
    print("data " * 10, data, sep="\n")
    addition = []
    hrefs = [data.get(key) for key in [('href_' + str(key)) for key in
                                       [i for i in range(1, data.get('num') + 1)]]]
    comments = [data.get(key) for key in
                [('comment_' + str(key)) for key in
                 [i for i in range(1, data.get('num') + 1)]]]
    link = iter(make_links_info_text(hrefs))
    comment = iter(comments)
    addition.append(md.text('shop: ', f"<code>{data['shop']}</code>"))
    for x in hrefs:
        new = md.text(next(link), ": ", f"{next(comment)}")
        addition.append(new)
    return addition


def get_id_from_text(text):
    id = re.search(r"#ID_(\d+)", text)
    if id:
        return id.group(1)
    else:
        return None


class TheWay:
    def __init__(self,id,way):
        self.id=id
        self.way=way


def find_the_way(message: types.Message) -> TheWay:
    print('start find way')
    text = message.reply_to_message.text
    id = re.search(r"#ID_(\d+)", text)
    if id:
        print('teleway')
        result = TheWay(id.group(1),'Telegram way')
        return result
    id = re.search(r"#WEB_(\d+)",text)
    if id:
        print('webway')
        result = TheWay(id.group(1),'Web way')
        return result
    else:
        return None

def make_message_text(message: list) -> md.text():
    print(message)
    result = []
    before = message[:1]
    after = message[1:]

    for is_answer, body in before:
        if is_answer:
            pointer = "✅"
            if len(body) > 50:
                body = str(body[:50]) + "..."
        else:
            pointer = "🆘"

        result.append(md.text(pointer, body, sep=" "))
        result.append(md.text(" "))

    for is_answer, body in after:
        if is_answer:
            pointer = ''
        else:
            pointer = '👈'
        if len(str(body)) >= 80:
            insert_text = str(body)[:60] + "..."
        else:
            insert_text = str(body)
        result.append(md.text(pointer, insert_text, sep=" "))
    return result

def make_message_text_w(message: list) -> md.text():
    print(message)
    result = []
    before = message[:1]
    after = message[1:]

    for is_answer, body in before:
        if is_answer:
            pointer = "✅"
            if len(body) > 50:
                body = str(body[:50]) + "..."
        else:
            pointer = "🆘"

        result.append(md.text(pointer, body, sep=" "))
        result.append(md.text(" "))

    for is_answer, body in after:
        if is_answer:
            pointer = '👉'
        else:
            pointer = '👈'
        if len(str(body)) >= 80:
            insert_text = str(body)[:60] + "..."
        else:
            insert_text = str(body)
        result.append(md.text(pointer, insert_text, sep=" "))
    return result




def check_lenght(text: list) -> list:
    while len(str(text)) > 4000:
        text.pop()
    return text


def make_message_text_full(message: list) -> md.text():
    message = check_lenght(message)
    result = []
    before = message[:1]
    after = message[1:]

    for is_answer,time, body in before:
        if is_answer:
            pointer = "✅"
        else:
            pointer = "🆘"
        result.append(md.text(pointer,time, body, sep=" "))
        result.append(md.text(" "))
    for is_answer,time, body in after:
        if is_answer:
            pointer = ''
        else:
            pointer = '👈'
        result.append(md.text(pointer,time, body, sep=" "))
    return result
