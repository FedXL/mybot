from aiogram import Dispatcher, types
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from sqlalchemy.engine.result import _TP
from sqlalchemy.orm import Session
from create_bot import bot, engine
from utils.statemachine import Admin
from typing import List, Tuple, Sequence
from sqlalchemy import delete, select, text, Row


def return_to_admin():
    buttons = [
        types.InlineKeyboardButton(text="↪️", callback_data="return_to_admin_menu"),
    ]
    keyword = types.InlineKeyboardMarkup(row_width=1)
    keyword.add(*buttons)
    return keyword


async def delete_message(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(f'Можно сразу несколько, если разделить запятой например: 1022, 1023,1024, 1025\n'
                                     f'Введите номер сообщения которое нужно удалить:', reply_markup=return_to_admin())
    await callback.answer("Вы в меню исправления ")
    await Admin.delete_manager_message.set()


def delete_messages(ids: List[int], session: Session) -> Sequence[Row[_TP]]:
    print('[INFO] start delete message')
    if len(ids) == 1:
        ids = ids[0]
        stmt = text("DELETE FROM messages WHERE id = :ids RETURNING message_id, storage_id;")
    elif len(ids) > 1:
        ids = tuple(ids)
        stmt = text("DELETE FROM messages WHERE id IN :ids RETURNING message_id, storage_id;")
    else:
        print('smth going wriong in delete_messages')
        raise TypeError
    print(stmt, ids)
    result = session.execute(stmt, {"ids": ids})
    deleted_messages = result.fetchall()
    print(deleted_messages)
    session.commit()
    return deleted_messages


async def delete_messages_handler(message: Message):
    print('[INFO] start delete message handler')
    try:
        ids = [int(message_id.strip(" ")) for message_id in message.text.split(",")]
        print(ids)
        count = 0
        with Session(engine) as session:
            deleted_messages = delete_messages(ids, session)
            print('[info] start delete messages')
            print(deleted_messages)
            for message_id, user_id in deleted_messages:
                print("[INFO] in delete messages user_id and message_id", user_id, message_id)
                try:
                    await bot.delete_message(user_id, message_id)
                    await bot.send_message(message.chat.id,
                                           f'Успешно удалено сообщение: {ids[count]}, {message_id}, {user_id}')
                except Exception as error:
                    await message.answer(f"Неудачно: {error}")
                count += 1
    except Exception as error:
        await message.answer(f"Что-то пошло не так : {error}")


def register_handlers_delete_manager_message(dp: Dispatcher):
    dp.register_callback_query_handler(delete_message, lambda c: c.data in ('delete_manager_message'),
                                       state=Admin.admin)
    dp.register_message_handler(delete_messages_handler, state=Admin.delete_manager_message)
