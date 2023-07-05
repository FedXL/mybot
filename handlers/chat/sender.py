import asyncio
import html
import io
import logging
import datetime
from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Regexp
from aiogram.types import ParseMode, CallbackQuery
from aiogram.utils import markdown
from base.base_connectors import insert_to_base, get_messages_from_base_last_5, get_from_base, get_target_message
from base.base_handlers_bot import add_photo_to_bd, add_doc_to_bd, check_is_kazakhstan
from create_bot import bot
import aiogram.utils.markdown as md
from handlers.admin.fast_answers import get_keyboard_answers_list
from sheets.add_orders import add_last_string
from utils.config import kazakhstan_chat, MANAGER, tradeinn_chat, alerts
from utils.texts import get_id_from_text, make_message_text, make_message_text_full, make_mask_to_messages, thank_u, \
    get_mask_from_message
from aiogram.types import Message
from utils.utils_lite import quot_replacer, disappear_message_message_is_send, create_new_message_order, \
    create_new_message_change, disappear_message_thanks_is_send


def get_keyboard_message_start():
    buttons = [
        types.InlineKeyboardButton(text="🗃", callback_data="message_menu"),
        types.InlineKeyboardButton(text="↕️️", callback_data="fast_answers_choice"),
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


def get_keyboard_fast_answer_menu():
    buttons = [
        types.InlineKeyboardButton(text="Ответы 🗣", callback_data="fast_answers_list"),
        types.InlineKeyboardButton(text="Карты 💳️", callback_data="fast_cards_list"),
        types.InlineKeyboardButton(text="🔼", callback_data="fast_back")
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard


def get_keyboard_menu_mess():
    buttons = [
        # types.InlineKeyboardButton(text="Забанить Гада 💔", callback_data="ban"),
        types.InlineKeyboardButton(text="✅ Завершено", callback_data='is_answered'),
        types.InlineKeyboardButton(text="🆘 Внимание", callback_data='is_not_answered'),
        # types.InlineKeyboardButton(text="🙏Спасибо🙏", callback_data='thanks'),
        types.InlineKeyboardButton(text="⚽️ Перекинуть", callback_data='change_channel'),
        types.InlineKeyboardButton(text="Full History", callback_data='full_history')
    ]
    keyword = types.InlineKeyboardMarkup(row_width=2)
    keyword.add(*buttons).\
        add(types.InlineKeyboardButton(text="↕️", callback_data="long_history")).\
        add(types.InlineKeyboardButton("🔼", callback_data="fast_back"))
    return keyword


async def change_message(message: Message, new_text: str):
    # Get the chat ID and message ID
    chat_id = message.chat.id
    message_id = message.message_id
    # Edit the message
    await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=new_text)


async def read_message(chat_id: int, message_id: int):
    message = await bot.get_message(chat_id=chat_id, message_id=message_id)
    text = message.text
    print(text)


async def catch_messaging(message: types.Message):
    """Надо её отрефакторить, но руки не доходят.
     первая половина ловит сообщения со стороны менеджеров
     втора половина со стороны пользователей."""

    try:
        message.text = html.escape(message.text)
    except Exception as er:
        print(er)

    if message.chat.type in ['group', 'channel', 'supergroup'] and message.reply_to_message:
        print('[INFO] from group start answer from admins')
        text_to_get_id = message.reply_to_message.text
        user_id_ = get_id_from_text(text_to_get_id)
        target_id_message = message.reply_to_message.message_id
        text_to_sheets = None

        if message.caption:
            manager_message = await bot.send_message(user_id_, message.caption)
            message_id = manager_message.message_id
            safe_caption = quot_replacer(message.caption)
            value2 = f"INSERT INTO messages (message_body,is_answer,storage_id,message_id) VALUES ('{safe_caption}',{True},{user_id_},{message_id});"
            insert_to_base(value2)

        if message.content_type == 'photo':
            print('[INFO] photo branch ')
            photo_id = message.photo[-1].file_id
            manager = MANAGER.get(message.from_user.id)
            text_to_sheets = "photo: " + photo_id
            manager_message = await bot.send_photo(user_id_, photo_id)
            message_id = manager_message.message_id
            add_photo_to_bd(photo_id, user_id_, message_id, True, manager)

        elif message.content_type == 'document':
            print("[INFO] document branch ")
            document_id = message.document.file_id
            manager = MANAGER.get(message.from_user.id)
            text_to_sheets = "doc: " + document_id
            manager_message = await bot.send_document(user_id_, document_id)
            message_id = manager_message.message_id
            add_doc_to_bd(document_id, user_id_, message_id, True, manager)

        elif message.content_type == 'text':
            print('[INFO] start text branch')
            text_to_send = message.text
            text_to_sheets = text_to_send
            manager = MANAGER.get(message.from_user.id)
            text_to_send = f"🔸 [{manager}]: " + text_to_send
            safe_text = quot_replacer(text_to_send)
            manager_message = await bot.send_message(user_id_, text_to_send)
            manager_message_id = manager_message.message_id
            value2 = f"INSERT INTO messages (message_body,is_answer,storage_id,message_id) VALUES ('{safe_text}',{True},{user_id_},{manager_message_id});"
            insert_to_base(value2)
        text_after_reply = get_messages_from_base_last_5(user_id_)
        text2 = make_message_text(text_after_reply)
        text1 = get_mask_from_message(text_to_get_id)

        response = await bot.send_message(message.chat.id, text=md.text(*text1, *text2, sep="\n"),
                                          parse_mode=ParseMode.HTML,
                                          reply_markup=get_keyboard_message_start())

        await bot.delete_message(message.chat.id, message.message_id)
        await bot.delete_message(message.chat.id, target_id_message)

        print("[INFO] new target message", response.message_id)
        valueh = f"UPDATE users SET message_id = {response.message_id} WHERE user_id = {user_id_};"
        insert_to_base(valueh)

        try:
            await add_last_string([(str(datetime.datetime.now()), manager, user_id_, text_to_sheets,)],
                                  'messages_storage')
        except Exception as ER:
            print(f"[ERROR] google sheets error in chat admins part : {ER}")

    # -----------------------------------------------------------------user part------------------------------------
    # ------------------------------------user part-----------------------------------------------------------------
    elif message.chat.type in ['private']:
        answer = check_is_kazakhstan(message.from_user.id)
        if answer == True:
            chat_switch = kazakhstan_chat
        else:
            chat_switch = tradeinn_chat

        if chat_switch == tradeinn_chat:
            await bot.send_message(alerts, f"From {message.from_user.first_name} | {message.from_user.id} | Message")


        print('[INFO] start chat from user is_kazakhstan:', answer)

        user_id = message.from_user.id
        user_name = message.from_user.first_name
        text_to_send = message.text

        safe_text = quot_replacer(text_to_send)
        print("[INFO]", user_id, user_name, message.text, sep="|")
        value1 = f"INSERT INTO users (user_id, user_name, message_id) VALUES ({user_id},'{user_name}', NULL);"
        insert_to_base(value1)

        if message.caption:
            print(f"[INFO] going message caption branch {message.caption}")
            safe_caption = quot_replacer(message.caption)
            value2 = f"INSERT INTO messages (message_body,is_answer,storage_id,message_id) VALUES ('{safe_caption}',{False}, {user_id},{message.message_id});"
            insert_to_base(value2)

        if message.content_type == "photo":
            print('[INFO] going photo branch ')
            photo_telegram_id = message.photo[-1].file_id
            add_photo_to_bd(photo_telegram_id, user_id, message.message_id)
            text_to_sheets = "photo: " + photo_telegram_id

        elif message.content_type == 'document':
            print('[INFO] going docs branch.')
            doc_id = message.document.file_id
            add_doc_to_bd(doc_id, user_id, message.message_id)
            text_to_sheets = "doc: " + doc_id

        elif message.content_type == 'text':
            print('[INFO] going text branch')
            message_id = message.message_id
            value2 = f"INSERT INTO messages (message_body, is_answer, storage_id,message_id) VALUES ('{safe_text}', {False}, {user_id},{message_id});"
            insert_to_base(value2)
            text_to_sheets = safe_text


        # ФОРМИРУЕМ ТЕКСТ ДЛЯ ОТПРАВКИ СООБЩЕНИЯ:
        message_list = get_messages_from_base_last_5(user_id)
        text = make_message_text(message_list)
        text_info = make_mask_to_messages(message, user_id)
        logging.info("[INFO] SEND FROM USER TO CHAT")
        # ОТПРАВЛЯЕМ СООБЩЕНИЕ В ГРУППУ

        response = await bot.send_message(chat_switch, md.text(
            text_info,
            md.text(*text, sep="\n"),
            sep="\n"),
                                          parse_mode=ParseMode.HTML,
                                          reply_markup=get_keyboard_message_start())
        await disappear_message_message_is_send(message)
        # СОХРАНЯЕМ ID отправленного сообщения ОНО НАМ ПОНАДОБИТСЯ ЧТО БЫ ПОТОМ БЫЛО ПОНЯТНО КАКОЕ СООБЩЕНИЕ УДАЛЯТЬ
        target_id = response.message_id
        print("[INFO] FROM RESPONSE!!!!!!!!!", target_id)
        # ВЫТАСКИВАЕМ СТАРЫЙ АЙДИ сообщения в группе ДЛЯ УНИЧТОЖЕНИЯ
        target = get_target_message(user_id)
        target = target[0][0]
        # УДАЛЯЕМ ПРОШЛОЕ СООБЩЕНИЕ И ОБНОВЛЯЕМ АЙДИ В БАЗЕ.
        if target:
            try:
                await bot.delete_message(chat_switch, target)
                print(f"[INFO] message killed success chat {chat_switch},target {target}")
            except Exception as er:
                print(f"[INFO] cant to kill message, {er}")
        value = f"UPDATE users SET message_id = {target_id} WHERE user_id = {user_id}"
        insert_to_base(value)
        try:
            await add_last_string([(str(datetime.datetime.now()), 'from user', message.from_user.id, text_to_sheets)],
                                  'messages_storage')
        except Exception as ER:
            print(f"[ERROR] google sheets error in chat admins part : {ER}")


async def open_long_history(callback_query: CallbackQuery):
    text_to_get_id = callback_query.message.text
    user_id = get_id_from_text(text_to_get_id)
    value = f"""SELECT is_answer,
                TO_CHAR(time + INTERVAL '3 hours', '[dd-MM HH24:mi]') AS formatted_datetime,
                message_body FROM messages WHERE storage_id={user_id} ORDER BY id DESC;"""
    text = get_from_base(value)
    text1 = get_mask_from_message(text_to_get_id)
    text2 = make_message_text_full(text)
    new_keyboard = types.InlineKeyboardMarkup(row_width=1)
    new_keyboard.add(types.InlineKeyboardButton("🔼", callback_data='fast_back_and_reload'))
    print ("we are here")
    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=md.text(*text1, *text2, sep="\n"),
        parse_mode=ParseMode.HTML
    )

    await bot.edit_message_reply_markup(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=new_keyboard)


async def comeback_from_history(callback_query: CallbackQuery):
    text_to_get_id = callback_query.message.text
    user_id = get_id_from_text(text_to_get_id)
    text1 = get_mask_from_message(text_to_get_id)
    text = get_messages_from_base_last_5(user_id)
    text2 = make_message_text(text)

    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=md.text(*text1, *text2, sep="\n"),
        parse_mode=ParseMode.HTML
    )

    await bot.edit_message_reply_markup(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=get_keyboard_menu_mess())


async def open_fast_answers(callback_query: CallbackQuery):
    print("[INFO] start open fast answers")
    match callback_query.data:
        case "fast_answers_choice":
            new_keyboard = get_keyboard_fast_answer_menu()
        case "message_menu":
            new_keyboard = get_keyboard_menu_mess()
        case 'fast_answers_list':
            print('[INFO] open_fast_answers: answer_list_branch')
            user_id = callback_query.from_user.id
            type_keyboard = "answer"
            new_keyboard = get_keyboard_answers_list(type_keyboard, user_id)
        case 'fast_cards_list':
            print('[INFO] open_fast_answers: card_list_branch')
            user_id = callback_query.from_user.id
            type_keyboard = 'card'
            new_keyboard = get_keyboard_answers_list(type_keyboard, user_id)
    await bot.edit_message_reply_markup(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=new_keyboard)
    await bot.answer_callback_query(callback_query.id, " ")


async def come_back(callback_query: CallbackQuery):
    new_keyboard = get_keyboard_message_start()
    await bot.edit_message_reply_markup(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        reply_markup=new_keyboard)
    await bot.answer_callback_query(callback_query.id, " ")


async def ban(callback_query: CallbackQuery):
    await callback_query.answer("Пока не работает")


async def send_fast_answer_to_user(callback_query: CallbackQuery):
    id = callback_query.data.split("_")[1]
    value = f"SELECT body FROM fast_answers WHERE id = {id};"
    text = get_from_base(value)[0][0]
    manager = MANAGER.get(callback_query.from_user.id)
    text = f"🔸 [{manager}]: " + text
    target_message_id = callback_query.message.message_id
    message_text = callback_query.message.text
    user_id = get_id_from_text(message_text)
    value = f"UPDATE users SET message_id = {target_message_id} WHERE user_id = {user_id};"  # обновляем айди сообщения в базе
    insert_to_base(value)
    # добавлям в цепочку сообщений сообщение в базе
    value = f"INSERT INTO messages (message_body,is_answer,storage_id) VALUES ('{text}',{True},{user_id});"
    insert_to_base(value)
    await bot.send_message(user_id, text)
    text1 = get_mask_from_message(message_text)
    text0 = get_messages_from_base_last_5(user_id)
    text2 = make_message_text(text0)

    await bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
        text=md.text(*text1, *text2, sep="\n"),
        parse_mode=ParseMode.HTML,
        reply_markup=get_keyboard_message_start()
    )
    print(target_message_id, message_text, sep="\n")
    await callback_query.answer("успешно")


async def is_answered(query: CallbackQuery):
    """метит основное сообщение зеленой меткой и сохраняет ответ в бд но не шлет пользователю."""
    # ИЗ этого текста вытаскивается id
    user_id_ = get_id_from_text(query.message.text)
    value1 = f"UPDATE users SET message_id = {query.message.message_id} WHERE user_id = {user_id_};"
    manager = MANAGER.get(query.from_user.id)
    if query.data == 'is_answered':
        text_to_send = "Завершено"
        is_answer = True
    elif query.data == 'is_not_answered':
        text_to_send = "Требует внимания"
        is_answer = False
    elif query.data == 'thanks':
        text_to_send = "🙏🙏🙏"
        is_answer = True
    else:
        print("[ERROR] querry data в is_answered пришла странная is_answered | is_not_answered", query.data)
    text_to_send = f"🔸 [{manager}]: " + text_to_send
    safe_text = quot_replacer(text_to_send)
    value2 = f"INSERT INTO messages (message_body,is_answer,storage_id) VALUES ('{safe_text}',{is_answer},{user_id_});"
    insert_to_base(value1 + value2)
    print('[INFO]', 'Bot send message to', user_id_, "text: ", text_to_send)
    text_after_reply = get_messages_from_base_last_5(user_id_)
    text2 = make_message_text(text_after_reply)
    text1 = get_mask_from_message(query.message.text)
    logging.info("[INFO] SEND FROM USER TO CHAT")
    chat_id = query.message.chat.id

    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=query.message.message_id,
        text=md.text(*text1, *text2, sep="\n"),
        parse_mode=ParseMode.HTML,
        reply_markup=get_keyboard_message_start()
    )


async def change_channel(query: CallbackQuery):
    user_id = get_id_from_text(query.message.text)
    print(f"[INFO] [start] change_channel  {user_id}")
    value = f"SELECT user_name, user_second_name,tele_username,is_kazakhstan FROM users WHERE user_id={user_id};"
    query_set = get_from_base(value)[0]
    before_answer = query_set[3]
    print('answer before', before_answer)
    if before_answer:
        answer = False
    else:
        answer = True
    print('answer after', answer)
    value = f"UPDATE users SET  is_kazakhstan = '{answer}' WHERE user_id = {user_id};"
    insert_to_base(value)
    new_message = create_new_message_change(query, user_id, query_set)
    await catch_messaging(new_message)
    await query.answer(query_set)
    await query.message.delete()
    before_chat = f"Error: before {before_answer}"
    after_chat = f"Error : after {answer}"

    if before_answer:
        before_chat = "KAZAKHSTAN"
    elif before_answer == False:
        before_chat = "TRADEINN"
    elif before_answer == None:
        before_chat = "TRADEINN"

    if answer:
        after_chat = "KAZAKHSTAN"
    elif answer == False:
        after_chat = "TRADEINN"

    await bot.send_message(query.message.chat.id, md.text(
        md.text("Администратор:", query.from_user.first_name),
        md.text("🥾⚽️ пользователя: ", user_id),
        md.text("Который раньше находился в чате :", before_chat),
        md.text("В чат: ", after_chat),
        sep="\n"
    ))


async def thanks_message(query: CallbackQuery):
    await is_answered(query)
    user_id = get_id_from_text(query.message.text)
    await query.answer("Успешно")
    await bot.send_message(user_id, thank_u())


async def extract_full_history(query: CallbackQuery):
    await query.answer("Full History")
    user_id = get_id_from_text(query.message.text)

    stmt = f"""SELECT
            id,
            TO_CHAR(time + INTERVAL '3 hours', 'dd-MM-YY HH24:mi') AS formatted_datetime,
            message_body 
            FROM messages
            WHERE storage_id = {user_id}
            ORDER BY id DESC;"""
    queryset = get_from_base(stmt)
    string = f"Клиент: {user_id} \n"
    for line in queryset:
        line_str = list(map(str, line))
        string += " ".join(line_str) + '\n'

    file = io.BytesIO(string.encode('utf-8'))
    file.name = f'history.txt'
    document_message = await bot.send_document(chat_id=query.message.chat.id, document=file,
                                               caption=markdown.text("История"))
    # Закрываем файл
    file.close()
    try:
        await asyncio.sleep(5 * 60)
        await document_message.delete()
    except:
        return


def register_handlers_warning(dp: Dispatcher):
    dp.register_callback_query_handler(come_back, lambda c: c.data == 'fast_back')
    dp.register_callback_query_handler(open_fast_answers, lambda c: c.data in (
    'fast_answers_choice', 'fast_cards_list', 'fast_answers_list', 'message_menu'))
    dp.register_callback_query_handler(comeback_from_history, lambda c: c.data == 'fast_back_and_reload')
    dp.register_callback_query_handler(open_long_history, lambda c: c.data == 'long_history')
    dp.register_callback_query_handler(extract_full_history, lambda c: c.data == 'full_history')
    dp.register_callback_query_handler(is_answered, lambda c: c.data in ('is_answered', 'is_not_answered'))
    dp.register_callback_query_handler(ban, lambda c: c.data == 'ban')
    dp.register_message_handler(catch_messaging, content_types=['text', 'photo', 'document'], )
    dp.register_callback_query_handler(send_fast_answer_to_user, Regexp('answer_([0-9]*)|card_([0-9]*)'))
    dp.register_callback_query_handler(thanks_message, lambda c: c.data == 'thanks')
    dp.register_callback_query_handler(change_channel, lambda c: c.data == 'change_channel')
