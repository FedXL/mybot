import asyncio
from typing import List

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ParseMode
import aiogram.utils.markdown as md
import datetime

from sqlalchemy import update
from sqlalchemy.orm import Session
from base.base_connectors import insert_and_get_from_base, insert_to_base
from base.base_handlers_bot import add_user_to_base
from base.models import OrderStatus
from create_bot import bot
from handlers.chat.sender import catch_messaging
from sheets.add_orders import add_last_string
from utils.config import orders_chat_storage, alerts, engine
from utils.markap_menu import SuperMenu
from utils.texts import make_user_info_report, order_answer_vocabulary, get_additional_from_proxi
from utils.utils_lite import create_new_message_order, quot_replacer


def check_parcer(order_id: int) -> List | None:
    with Session(engine) as session:
        result = session.query(OrderStatus.order_price).filter(OrderStatus.order_id == order_id).one_or_none()
        session.close()
    return result


async def make_order_answer(query: CallbackQuery, state: FSMContext):
    await query.answer("Успешно")
    await query.message.delete_reply_markup()
    await query.message.delete()
    income = query.data
    login_tradeinn, pass_tradeinn = False, False
    match income:
        case "KAZ_ORDER_LINKS":
            async with state.proxy() as data:
                try:
                    addition = get_additional_from_proxi(data)
                except:
                    addition = "ERROR"
                    print(data)
        case "KAZ_ORDER_CABINET":
            async with state.proxy() as data:
                addition = [
                    md.text('Магазин: ', f"<code>{data.get('shop')}</code>"),
                    md.text('Логин: ', f"<code>{data.get('log')}</code>"),
                    md.text('Пароль: ', f"<code>{data.get('pass')}</code>"),
                ]
        case "TRADEINN":
            async with state.proxy() as data:
                login_tradeinn = data.get('login')
                pass_tradeinn = data.get('pass')
                addition = [
                    md.text('Логин: ', f"<code>{login_tradeinn}</code>"),
                    md.text("Пaроль: ", f"<code>{pass_tradeinn}</code>")
                ]
                await bot.send_message(alerts, f"From {query.from_user.username} | {query.from_user.id} | NewOrder!")
        case "PAYMENT":
            async with state.proxy() as data:
                addition = [
                    md.text('Магазин: ', f"<code>{data.get('shop')}</code>"),
                    md.text('Логин: ', f"<code>{data.get('login')}</code>"),
                    md.text('Пароль: ', f"<code>{data.get('pass')}</code>"),
                ]
    await state.finish()

    ## ------------------------------- ADD TO BASE - ----------------------------------------
    new_str = quot_replacer(str(addition))

    # эта штука кошмарна , но она добавляет пометку is_kazakhstan в users
    add_user_to_base(query.from_user.id,
                     income,
                     query.from_user.first_name,
                     query.from_user.last_name,
                     query.from_user.username)

    try:
        order_info = f"INSERT INTO orders (client,type,body,time) VALUES ({query.from_user.id},'{income}','{new_str}', NOW()) RETURNING id;"
        order_id: int = insert_and_get_from_base(order_info)[0][0]
        add_order_status = f'INSERT INTO order_status (order_id,status) VALUES ({order_id}, {True});'
        insert_to_base(add_order_status)
        new_message = create_new_message_order(query, income, order_id)
        await catch_messaging(new_message)
        if income == "TRADEINN":
            stmt = f"INSERT INTO parce_task(order_id,login,password,type) VALUES ({order_id},'{login_tradeinn}','{pass_tradeinn}','TRADEINN');"
            insert_to_base(stmt)
    except Exception as er:
        order_id = False
        print("[ERROR] ORDER didnt was SAVED IN save_orders.orders_callback 52 string", er)
    user_info = make_user_info_report(query, order_id)
    pre_additional = order_answer_vocabulary(income, order_id)

    await_message = await bot.send_message(query.from_user.id, "Нам надо проверить данные.")
    await asyncio.sleep(2)
    time = 0
    # ----------------------------Tradeinn--------------------------------------------------
    if income == 'TRADEINN':
        #прости меня господи:
        while True:
            if 30 > time >= 0:
                textss = "Проверям данные. "
            elif 60 > time >= 30:
                textss = "Проверям, мы на пол пути. "
            elif 90 > time >= 60:
                textss = "Осталось чуть-чуть. "
            elif 200 > time >= 90:
                textss = "Видимо вы не первый в очереди, придется еще подождать."
            elif time > 200:
                textss = "Успех"
                await await_message.edit_text(f"{textss}")
                await bot.send_message(orders_chat_storage, md.text(
                    md.text('parcing long ERROR 200 sec left and nothing'),
                    md.text(user_info),
                    md.text(*addition, sep="\n"),
                    sep="\n"),
                                       disable_web_page_preview=True,
                                       parse_mode=ParseMode.HTML)

                await bot.send_message(query.from_user.id, md.text(
                    md.text("Ваш заказ успешно принят."),
                    md.text(*pre_additional, sep="\n"),
                    md.text(*addition, sep="\n"),
                    sep="\n"),
                                       reply_markup=SuperMenu.cancel,
                                       disable_web_page_preview=True,
                                       parse_mode=ParseMode.HTML)
                break

            await asyncio.sleep(5)
            time += 5
            await await_message.edit_text(f"{textss}...{time}/100")
            price = check_parcer(order_id)[0]
            print(price)

            ##----------------------------------кривой пароль
            if price == "Incorrect password":
                delete_order_from_head(order_id)
                await await_message.edit_text(("Неправильный логин или пароль"))
                await bot.send_message(query.from_user.id, md.text(
                    md.text(*addition, sep="\n"),
                    sep="\n"), parse_mode=ParseMode.HTML)
                await bot.send_message(orders_chat_storage, md.text(
                    md.text('Неправильный пароль'),
                    md.text(user_info),
                    md.text(*addition, sep="\n"),
                    sep="\n"),
                                       disable_web_page_preview=True,
                                       parse_mode=ParseMode.HTML)
                break
            ##----------------------------------- в ордер статусе ниче нет
            elif price is None:
                continue
            ##------------------------------------ все окей
            elif type(price) == str and price != 'ERROR':
                await await_message.delete()
                await bot.send_message(query.from_user.id, md.text(
                    md.text("Ваш заказ успешно принят."),
                    md.text(*pre_additional, sep="\n"),
                    md.text(*addition, sep="\n"),
                    sep="\n"),
                                       reply_markup=SuperMenu.cancel,
                                       disable_web_page_preview=True,
                                       parse_mode=ParseMode.HTML)
                await bot.send_message(orders_chat_storage,
                                       md.text(md.text(user_info),
                                               md.text(*addition, sep="\n"),
                                               sep="\n"),
                                       disable_web_page_preview=True,
                                       parse_mode=ParseMode.HTML)
                try:
                    await add_last_string(
                        [(order_id, query.from_user.id, str(datetime.datetime.now()), income, new_str)],
                        'orders_storage')
                    if income in ['KAZ_ORDER_LINKS', 'KAZ_ORDER_CABINET']:
                        await add_last_string(
                            [(order_id, query.from_user.id, str(datetime.date.today()), income, new_str)],
                            'Dashboard')
                except Exception as ER:
                    print(f"[ERROR] google sheets error in orders callback: {ER}")
                break
            ##------------------------------------------------------ОШИБКА
            elif price == 'ERROR':
                delete_order_from_head(order_id)
                await await_message.edit_text('Успешно')
                await bot.send_message(orders_chat_storage, md.text(
                    md.text('Parcing ERROR'),
                    md.text(user_info),
                    md.text(*addition, sep="\n"),
                    sep="\n"),
                                       disable_web_page_preview=True,
                                       parse_mode=ParseMode.HTML)

                break
    # ----------------------------------------ВСЁ остальное-----------------------------------------------------------------------

    else:
        await bot.send_message(query.from_user.id, md.text(
            md.text("Ваш заказ успешно принят."),
            md.text(*pre_additional, sep="\n"),
            md.text(*addition, sep="\n"),
            sep="\n"),
                               reply_markup=SuperMenu.cancel,
                               disable_web_page_preview=True,
                               parse_mode=ParseMode.HTML)

        await bot.send_message(orders_chat_storage,
                               md.text(md.text(user_info),
                                       md.text(*addition, sep="\n"),
                                       sep="\n"),
                               disable_web_page_preview=True,
                               parse_mode=ParseMode.HTML)
        try:
            await add_last_string([(order_id, query.from_user.id, str(datetime.datetime.now()), income, new_str)],
                                  'orders_storage')
            if income in ['KAZ_ORDER_LINKS', 'KAZ_ORDER_CABINET']:
                await add_last_string([(order_id, query.from_user.id, str(datetime.date.today()), income, new_str)],
                                      'Dashboard')

        except Exception as ER:
            print(f"[ERROR] google sheets error in orders callback: {ER}")


def delete_order_from_head(order_id: int):
    print('[INFO] start delete_order_from_head')
    try:
        with Session(engine) as session:
            is_head = session.query(OrderStatus).filter(OrderStatus.order_id == order_id).scalar()
            if is_head:
                status = False
            else:
                status = True
            stmt = update(OrderStatus).filter(OrderStatus.order_id == order_id).values(status=status)
            session.execute(stmt)
            session.commit()
            print(f'[INFO] success the {order_id} provide status {status}')
    except Exception as ER:
        print(f'delete_order_from_head Error {ER}')


def register_handlers_save_order(dp: Dispatcher):
    dp.register_callback_query_handler(make_order_answer,
                                       lambda c: c.data in ['KAZ_ORDER_LINKS', 'KAZ_ORDER_CABINET', 'TRADEINN',
                                                            'PAYMENT'],
                                       state="*")
