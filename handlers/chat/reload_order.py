from aiogram import types, Dispatcher
from aiogram.dispatcher import filters
from aiogram.dispatcher.filters import Regexp
from aiogram.types import ParseMode
import aiogram.utils.markdown as md
from sqlalchemy import func, update
from sqlalchemy.orm import Session
from base.base_connectors import get_from_base, insert_to_base
from base.models import OrderStatus, Order, Discount
from create_bot import bot
from handlers.save_orders.orders_callback import delete_order_from_head
from utils.config import ADMINS, engine
from utils.utils_lite import disappear_message


async def check_parsing_status(message, order_id):
    print('[INFO] check parsing status start')
    with Session(engine) as session:
        order_price = session.query(OrderStatus.order_price).filter(OrderStatus.order_id == order_id).one_or_none()
    print('order_price', order_price)
    if not order_price[0]:
        print("подождите минутку заказ ещё не проверен")
        report_message = await message.answer('Подождите минутку, заказ ещё не проверен')
        await disappear_message(report_message, 60)
        return False
    elif order_price[0] == "Incorrect password":
        print('Неправильное имя или пароль. Требуйте проверить данные у пользователя')
        report_message = await message.answer(
            'Неправильное имя или пароль. Требуйте у пользователя проверить данные и '
            'сделать ещё один заказ.')
        await disappear_message(report_message, 60)
        return False
    elif order_price[0] == 'ERROR':
        report_message = await message.answer('Ошибка парсинга. Зовите Фёдора.')
        await disappear_message(report_message, 60)
        return False
    else:
        return True


async def check_way_order_reloader(message: types.Message, regexp_command):
    """
    проверить есть ли или нет

    if in ADMINS - > check permission -> reload order
    if not in ADMINS -> check 24 (return if not) -> check permission -> reload order
    """
    print('[INFO] start check_way_order_reloader')
    order_id = regexp_command.group(1)
    await message.delete()

    with Session(engine) as session:
        order_type = session.query(Order.type).filter(Order.id == order_id).scalar()
        print(order_type)

    if order_type == 'TRADEINN':
        if not await check_parsing_status(message, order_id):
            return
    if message.from_user.id not in ADMINS:
        stmt_check = f"""
                    SELECT CASE
                    WHEN time < now() - interval '24 hour' 
                    THEN 'false'
                    ELSE 'true'
                    END AS is_recent
                    FROM orders WHERE id = {order_id};"""
        check_answer = get_from_base(stmt_check)
        if check_answer:
            check_answer = check_answer[0][0]
            if check_answer == 'false':
                stmt_find_user = f"""
                                SELECT client
                                FROM orders
                                WHERE id = {order_id}
                                """
                client_id = get_from_base(stmt_find_user)[0][0]
                error_message = await message.answer(f"Отказано в доступе. \n"
                                                     f"Прошло более 24 часов. \n"
                                                     f"Заказ: <code> {order_id} </code> \n"
                                                     f"Клиент: <code>{client_id}</code>",
                                                     parse_mode=ParseMode.HTML)
                await disappear_message(error_message)
                return
    await secure_order(message, order_id)


async def catch_callback_order_reloader(callback: types.CallbackQuery):
    await callback.answer("Успех")
    data = callback.data.split("_")
    order_id = data[1]
    with Session(engine) as session:
        order_type = session.query(Order.type).filter(Order.id == order_id).scalar()
        stmt = update(OrderStatus).where(OrderStatus.order_id == order_id).values(manager_id=callback.from_user.id)
        session.execute(stmt)
        session.commit()

    if order_type in ["KAZ_ORDER_LINKS", "KAZ_ORDER_CABINET", "PAYMENT"]:
        await callback.message.delete()
        await order_reloader(callback.message, order_id)
        send_message = await bot.send_message(callback.message.chat.id,
                                              f'Заказ успешно закреплён за {callback.from_user.username}')
        await disappear_message(send_message, 30)
        return

    message_to_clean = await callback.message.edit_text(
        f'Успешно теперь заказ закреплён за {callback.from_user.username}')

    # --------------------------------------------------------------------------------- IGoR костыль------------------
    if callback.from_user.id == 350946841:
        await igor_order_reloader(callback.message, order_id)
    await disappear_message(message_to_clean, 30)


async def igor_order_reloader(message: types.Message, order_id):
    try:
        value = f"SELECT type, body, client FROM orders WHERE id = {order_id};"
        query = get_from_base(value)[0]
        query_set = query[1]
        name = query[0]
        client = "Клиент : " + str(query[2])
        query_set = query_set[1:-1].split(",")
        new_query = [f"Заказ – {order_id}", name, client]
        for i in query_set:
            a = i.strip().strip("'")
            new_query.append(a)
        value = f"SELECT status FROM order_status WHERE order_id = {order_id};"
        in_works = get_from_base(value)[0][0]
        order_message = await bot.send_message(350946841, md.text(*new_query, sep='\n'),
                                               parse_mode=ParseMode.HTML)
    except Exception as ER:
        print("[ERROR] ", ER)
        order_message = await bot.send_message(message.chat.id,
                                               f"РћС€РёР±РєР° Р·Р°РєР°Р·Р° РЅРѕРјРµСЂ {order_id} РЅРµС‚ РІ Р±Р°Р·Рµ.\n"
                                               f"РІ Р±Р°Р·Рµ РІРµСЂРЅСѓР»РѕСЃСЊ: {query}, \n ERROR: {ER}")
    await disappear_message(order_message)


# ----------------------------------------------------------------------------------------- костыль end


async def order_reloader(message: types.Message, order_id):
    try:
        value = f"SELECT type, body, client FROM orders WHERE id = {order_id};"
        query = get_from_base(value)[0]
        query_set = query[1]
        name = query[0]
        client = "Клиент : " + str(query[2])
        query_set = query_set[1:-1].split(",")
        new_query = [f"Заказ – {order_id}", name, client]
        for i in query_set:
            a = i.strip().strip("'")
            new_query.append(a)
        value = f"SELECT status FROM order_status WHERE order_id = {order_id};"
        order_message = await bot.send_message(message.chat.id, md.text(*new_query, sep='\n'),
                                               parse_mode=ParseMode.HTML)
    except Exception as ER:
        print("[ERROR] ", ER)
        order_message = await bot.send_message(message.chat.id,
                                               f"РћС€РёР±РєР° Р·Р°РєР°Р·Р° РЅРѕРјРµСЂ {order_id} РЅРµС‚ РІ Р±Р°Р·Рµ.\n"
                                               f"РІ Р±Р°Р·Рµ РІРµСЂРЅСѓР»РѕСЃСЊ: {query}, \n ERROR: {ER}")
    await disappear_message(order_message)


async def secure_order(message: types.Message, order_id:int):
    buttons = [
        types.InlineKeyboardButton(text="Закрепить/Перезакрепить", callback_data=f'secureOrder_{order_id}')]

    keyword = types.InlineKeyboardMarkup(row_width=1)
    keyword.add(*buttons)
    info = collect_info(order_id=order_id)

    stmt2 = f"""SELECT managers.short_name FROM order_status
                                    JOIN managers ON order_status.manager_id = managers.user_id
                                    WHERE order_status.order_id = {order_id};"""
    short_name = get_from_base(stmt2)
    with Session(engine) as session:
        order_price = session.query(OrderStatus.order_price).filter(OrderStatus.order_id == order_id).one_or_none()
        order_price = order_price[0]
    if short_name:
        manager_str = "уже закреплён за другим менеджером " + "[" + str(
            short_name[0][0]) + "]." + "\n" + "Перезакрепить менеджера?"
    else:
        manager_str = "Ещё не закреплён за менеджером. Закрепить за Вами?"

    await bot.send_message(message.chat.id, md.text(
        md.text("Менеджер: ", manager_str),
        md.text("Заказ №: ", order_id),
        md.text("Сумма заказа: ", order_price),
        md.text(f"Клиент: {info['client']}"),
        md.text(f"VIP:  {info['VIP']}"),
        md.text(f"Заказы: {info['orders_summary']} шт."),
        md.text(f"Накоплено: {info['money_summary']} руб."),
        sep='\n'
    ),
                           reply_markup=keyword)


def collect_info(order_id):
    with Session(engine) as session:
        client_id = session.query(Order.client).filter(Order.id == order_id).scalar()
        orders_summary = session.query(func.count()).filter(Order.client == client_id).scalar()
        query = session.query(Order, OrderStatus).filter(Order.id == OrderStatus.order_id).filter(
            Order.client == client_id).all()
        VIP = session.query(Discount.is_vip).filter(Discount.user_id == client_id).one_or_none()
        summ = 0
        lose = ['Incorrect password', None, 'Не вышло залогиниться', 'ERROR', 'Не вышло.']
        for i in query:
            price = i.OrderStatus.order_price
            if price not in lose:
                summ += float(price.split(' ')[0])
        summ = int(summ)
        formatted_number = '{:.2f}'.format(summ)

        result = {'client': client_id,
                  'orders_summary': orders_summary,
                  'money_summary': formatted_number,
                  'VIP': VIP}
        return result

async def delete_handler_order_from_head(message: types.Message):
    data = message.text.split("_")
    order_id: int = data[1]
    delete_order_from_head(order_id)
    await message.delete()
    send_message = await bot.send_message(message.chat.id,'Успешно')
    await disappear_message(send_message,5)
def register_reload_order(dp: Dispatcher):

    dp.register_message_handler(check_way_order_reloader,
                                filters.RegexpCommandsFilter(regexp_commands=['order_([0-9]*)']))
    dp.register_callback_query_handler(catch_callback_order_reloader, Regexp('lookOrder_([0-9])*|secureOrder_([0-9])*'))
    dp.register_message_handler(delete_handler_order_from_head, filters.RegexpCommandsFilter(regexp_commands=['head_([0-9]*)']))
