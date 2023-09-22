from aiogram import Dispatcher, types
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, ParseMode
from aiogram.dispatcher import FSMContext
from base.base_connectors import insert_to_base, get_from_base, insert_and_get_from_base
from create_bot import bot
from handlers.admin.faq_upload import welcome_to_admin_mode
from utils.config import ADMINS
from utils.statemachine import Admin
from utils.utils_lite import quot_replacer, disappear_message
import aiogram.utils.markdown as md


def answer_change_menu(return_button: str):
    print("[INFO] [START] get_answer_change_menu", return_button)
    assert return_button in ["card", "answer"]
    keyboard = types.InlineKeyboardMarkup()
    buttons = [
        types.InlineKeyboardButton(text="Изменить название", callback_data="change_button"),
        types.InlineKeyboardButton(text="Изменить текст", callback_data="change_answer")
    ]
    keyboard.add(types.InlineKeyboardButton(text="Удалить", callback_data="delete_answer")).add(*buttons)

    match return_button:
        case 'card':
            keyboard.add(types.InlineKeyboardButton(text="↪️", callback_data="cards_expand"))
        case 'answer':
            keyboard.add(types.InlineKeyboardButton(text="↪️", callback_data="answers_expand"))
    return keyboard


def get_keyboard_answers_menu(type_answer):
    print("[INFO] [START] get_keyboard_answers_meny: ", type_answer)
    keyword = types.InlineKeyboardMarkup(row_width=1)
    match type_answer:
        case "answer":
            buttons = [
                types.InlineKeyboardButton(text="Добавить ответ", callback_data="add_answer"),
                types.InlineKeyboardButton(text="↕️", callback_data="answers_expand"),
                types.InlineKeyboardButton(text="↪️", callback_data="return_to_admin_menu")]
        case "card":
            buttons = [
                types.InlineKeyboardButton(text="Добавить карту", callback_data="add_card"),
                types.InlineKeyboardButton(text="↕️", callback_data="cards_expand"),
                types.InlineKeyboardButton(text="↪️", callback_data="return_to_admin_menu")]

    keyword.add(*buttons)
    return keyword


def assemble_the_keyboard(query, type_answer:str) -> types.InlineKeyboardMarkup:
    print("[INFO] [START] start_assemble_the_keyboard")
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    print("[INFO] type of answer: ", type_answer)
    if type_answer == "card":
        callback_for_return_button = "fast_cards_menu_admin"
        callback_salt=""
    elif type_answer == 'answer':
        callback_for_return_button = "fast_answers_menu_admin"
        callback_salt = ""
    elif type_answer == 'cards_in_message':
        callback_for_return_button = "fast_answers_choice"
        callback_salt = "card_"
    elif type_answer == 'answers_in_message':
        callback_for_return_button = "fast_answers_choice"
        callback_salt = "answer_"
    else:
        raise TypeError

    for count, (answer_id, answer_body) in enumerate(query, start=1):
        text = str(answer_body)[:30] + "..." if len(str(answer_body)) > 30 else str(answer_body)
        callback_data = callback_salt + str(answer_id)
        button = InlineKeyboardButton(text=f"{count}. {text}", callback_data=str(callback_data))
        keyboard.add(button)

    keyboard.add(types.InlineKeyboardButton(text="🔼", callback_data=callback_for_return_button))
    print('[INFO] [END] assemble_the_keyboard ')
    return keyboard


def full_list_answer_keyboard_for_admin(user: int, type_answer: str) -> types.InlineKeyboardMarkup():
    print(f"[INFO] [START] full_list_answer_keyboard_for_admin: start user={user}, type_of_answer={type_answer}")
    assert type_answer in ['card', 'answer']
    assert isinstance(user, int)
    match type_answer:
        case "answer":
            if user in ADMINS:
                value = "SELECT id, button_name FROM fast_answers WHERE type = 'answer' ORDER BY id;"
            else:
                value = f"SELECT id, button_name " \
                        f"FROM fast_answers " \
                        f"WHERE manager = '{user}'" \
                        f"AND type='{type_answer}' ORDER " \
                        f"BY id;"
            query = get_from_base(value)
        case "card":
            if user in ADMINS:
                value = "SELECT id, button_name FROM fast_answers WHERE type = 'card' ORDER BY id;"
            else:
                value = f"SELECT id, button_name " \
                        f"FROM fast_answers " \
                        f"WHERE manager = '{user}'" \
                        f"AND type='{type_answer}' ORDER " \
                        f"BY id;"
            query = get_from_base(value)

    return assemble_the_keyboard(query, type_answer)


def get_keyboard_answers_list(type_answer:str, user_id:int):
    """клавиатура для sender"""
    print("[INFO] get_keyboard_answers_list: start foo")
    assert type_answer in ["card","answer"]
    assert isinstance(user_id, int)
    match type_answer:
        case "card":
            stmt = f"SELECT id, button_name FROM fast_answers WHERE type = '{type_answer}' ORDER BY manager;"
            type_of_keyboard = "cards_in_message"
        case "answer":
            stmt = f"SELECT id,button_name FROM fast_answers WHERE type = '{type_answer}' AND manager = {user_id} ORDER BY id;"
            type_of_keyboard = "answers_in_message"
    query = get_from_base(stmt)

    return assemble_the_keyboard(query,type_of_keyboard)



async def fast_answers_menu(callback_query: CallbackQuery):
    print('[INFO] [START] fast_answers_admin')
    match callback_query.data:
        case "fast_answers_menu_admin":
            await callback_query.answer("Answer menu")
            await Admin.answers.set()
            await callback_query.message.edit_text("Вы в меню быстро-ответов",
                                                   reply_markup=get_keyboard_answers_menu('answer'))
        case "fast_cards_menu_admin":
            await callback_query.answer("Card menu")
            await Admin.answers.set()
            await callback_query.message.edit_text("Вы в меню кредитных карт",
                                                   reply_markup=get_keyboard_answers_menu('card'))


async def get_full_list_fast_answers(callback_query: types.CallbackQuery, type_answer=None):
    """ возвращает список карт или список быстроответов"""
    print("[INFO][START] fast_answers_admin_expand:", callback_query.data)
    assert callback_query.data in ['answers_expand','cards_expand','delete_answer']
    match callback_query.data:
        case "answers_expand":
            name = 'answer'
            text = 'Быстроответы: '
            await callback_query.answer("Answer menu")
        case "cards_expand":
            name = 'card'
            text = 'Карты: '
            await callback_query.answer("Card menu")

    if type_answer:
        name = type_answer
        if name == 'card':
            text = 'Карты'
        elif name == 'answer':
            text = 'Быстроответы'
    print(type_answer)
    print(name, text)
    await callback_query.message.edit_text(text,
            reply_markup=full_list_answer_keyboard_for_admin(callback_query.from_user.id, name))


async def add_name(callback_query: CallbackQuery):
    await callback_query.answer("Добавить название кнопки")
    await bot.send_message(callback_query.from_user.id, "Введите название быстроответа.")


async def catch_changed_answer(message_or_callback: Message | CallbackQuery, state: FSMContext):
    """функция ловит колбэк из меню изменения быстроответа"""
    print("[INFO] [START] catch_changed_answer: start")
    state_status = await state.get_state()

    if isinstance(message_or_callback, types.CallbackQuery):
        print("[INFO] catch_changed_answer: callback branch")
        user_id = message_or_callback.message.from_user.id
        print(user_id)
    elif isinstance(message_or_callback, types.Message):
        print("[INFO] catch_changed_answer: message catch branch")
        user_id = message_or_callback.from_user.id
        text = message_or_callback.text
        safe_text = quot_replacer(text)
        async with state.proxy() as data:
            id = data.get('id')

    if state_status == "Admin:change_answer":
        value = f"UPDATE fast_answers SET body = '{safe_text}' WHERE id = {id} RETURNING type;"
        result = insert_and_get_from_base(value)
    elif state_status == "Admin:change_button":
        value = f"UPDATE fast_answers SET button_name = '{safe_text}' WHERE id = {id} RETURNING type;"
        result = insert_and_get_from_base(value)

    if result:
        result = result[0][0]
    await make_personal_answer_handler(message_or_callback, state, result, id)


async def make_personal_answer_handler(callback_or_message: CallbackQuery | Message, state: FSMContext,
                                       type_answer=None, answer_id=None):
    print(f"[INFO] [START] make_personal_answer_handler ")
    assert type_answer in ['card', 'answer',None]
    if answer_id:
        id = answer_id
    else:
        id = callback_or_message.data

    if not type_answer:
        value = f"SELECT body,button_name,type FROM fast_answers WHERE id = {id};"
        query = get_from_base(value)[0]
        type_answer = query[2]
    else:
        value = f"SELECT body,button_name FROM fast_answers WHERE id = {id};"
        query = get_from_base(value)[0]
    text = query[0]
    name = query[1]

    mdtext = md.text(
        md.text("Название кнопки: "),
        md.text("<code>", name, "</code>"),
        md.text("Текст быстроответа: "),
        md.text("<code>", text, "</code>"),
        md.text("Удалить или Изменить желаете?"),
        sep="\n")

    if isinstance(callback_or_message, types.CallbackQuery):
        print("[INFO] make_personal_answer_handler: callback branch")
        await callback_or_message.answer('Меню ответа')
        await callback_or_message.message.edit_text(mdtext,
                                                    parse_mode=ParseMode.HTML,
                                                    reply_markup=answer_change_menu(type_answer))
        async with state.proxy() as data:
            data['id'] = id
        await Admin.answers.set()

    elif isinstance(callback_or_message, types.Message):
        print("[INFO] make_personal_answer_handle message branch")
        await callback_or_message.delete()
        await bot.send_message(callback_or_message.from_user.id, mdtext,
                               parse_mode=ParseMode.HTML,
                               reply_markup=answer_change_menu(type_answer))
        await Admin.answers.set()
        async with state.proxy() as data:
            data['id'] = id


async def add_answer(callback_query: CallbackQuery, state):
    print("[INFO] [START] add_answer: start")
    assert callback_query.data in ['add_answer', 'add_card']
    match callback_query.data:
        case "add_answer":

            value = f"INSERT INTO fast_answers(body,button_name,type,manager) VALUES ('null','null','answer',{callback_query.from_user.id})" \
                    f"RETURNING id;"
            id = insert_and_get_from_base(value)[0][0]
            type_of_answer = 'answer'
            await callback_query.answer('Успешно')
            print('[INFO] add_answer: ', state, type_of_answer, id)
            await make_personal_answer_handler(callback_query, state, type_of_answer, id)
        case "add_card":
            type_of_answer = 'card'
            value = f"INSERT INTO fast_answers(body,button_name,type,manager) VALUES ('null','null','card',{callback_query.from_user.id})" \
                    f"RETURNING id;"
            id = insert_and_get_from_base(value)[0][0]
            await callback_query.answer('Успешно')
            print('[INFO] add_answer: ', state, type_of_answer, id)
            await make_personal_answer_handler(callback_query, state, type_of_answer, id)


async def start_change_answer(callback_query: CallbackQuery, state: FSMContext):
    print("[INFO] [START] start change answer")
    async with state.proxy() as data:
        id = data.get('id')
        print("id  ********************", id)
    smt = f"SELECT type FROM fast_answers WHERE id = '{id}';"
    type_answer = get_from_base(smt)[0][0]
    match callback_query.data:
        case 'delete_answer':
            print("[INFO] case DELETE")
            value = f"DELETE FROM fast_answers WHERE id = {id};"
            insert_to_base(value)
            await Admin.answers.set()
            await get_full_list_fast_answers(callback_query, type_answer)
        case 'change_answer':
            print("[INFO] case CHANGE answer")
            message = await callback_query.message.edit_text("Введите новый текст: ")
            await Admin.change_answer.set()
            await disappear_message(message, 90)
        case 'answers_comeback':
            print("[INFO] case COMEBACK")
            await Admin.answers.set()
            await get_full_list_fast_answers(callback_query, type_answer)
        case 'change_button':
            print('[INFO] case CHANGE button')
            message = await callback_query.message.edit_text("Введите новое название: ")
            await Admin.change_button.set()
            await disappear_message(message, 90)


def register_handlers_fast_answers(dp: Dispatcher):
    dp.register_callback_query_handler(fast_answers_menu,
                                       lambda c: c.data in ('fast_answers_menu_admin', "fast_cards_menu_admin"),
                                       state=[Admin.admin, Admin.answers])
    dp.register_callback_query_handler(get_full_list_fast_answers,
                                       lambda c: c.data in ('answers_expand', 'cards_expand'),
                                       state=Admin.answers)
    dp.register_callback_query_handler(add_answer, lambda c: c.data in ('add_answer', 'add_card'), state=Admin.answers)

    dp.register_callback_query_handler(start_change_answer, lambda c: c.data in (
        'delete_answer', 'change_answer', 'answers_comeback', 'change_button'), state=[Admin.answers])
    dp.register_message_handler(catch_changed_answer, state=[Admin.change_answer, Admin.change_button])
    dp.register_callback_query_handler(welcome_to_admin_mode, lambda c: c.data in ('return_to_admin_menu'), state="*")

    dp.register_callback_query_handler(make_personal_answer_handler, state=Admin.answers)
