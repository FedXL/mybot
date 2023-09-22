import asyncio
import html

from aiogram.dispatcher import FSMContext

from sqlalchemy import delete
from sqlalchemy.orm import Session
from base.base_handlers_bot import add_post_to_base
from base.models import Posts
from utils.config import supported_channel, supported_bot, engine, love_is
from utils.posts_bot import send_message, delete_message, edit_message, send_message_text, send_photo_message, \
    send_video_message
from utils.statemachine import Admin
from aiogram import Dispatcher, types
from aiogram.types import Message, CallbackQuery, ParseMode
from create_bot import bot, bot_for_support
from aiogram.dispatcher.filters import Regexp


class GetKeyboard:
    def __init__(self, message_id=None):
        self.message_id = message_id

    class Hello:
        def __get__(self, instance, owner) -> types.InlineKeyboardMarkup:
            buttons = [
                types.InlineKeyboardButton(text="Редактировать пост.", callback_data="edit_post"),
                types.InlineKeyboardButton(text="Создать новый пост.", callback_data='create_post'),
                types.InlineKeyboardButton(text="↪️", callback_data="return_to_admin_menu")
            ]
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(*buttons)
            return keyboard

    class Proof:
        def __get__(self, instance, owner):
            buttons = [
                types.InlineKeyboardButton(text="Верно. Отправить пост в канал.", callback_data="create_post_finnaly"),
                types.InlineKeyboardButton(text="Отмена.", callback_data='return_to_admin_menu')
            ]
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(*buttons)
            return keyboard

    class Button:
        def __get__(self, instance, owner):
            buttons = [types.InlineKeyboardButton(text="Заказать", url="https://t.me/ShipKZ_bot")]
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(*buttons)
            return keyboard

    class Edit:
        def __get__(self, instance, owner):
            with Session(engine) as session:
                query = session.query(Posts).all()
            buttons = []
            for post in query:
                button = types.InlineKeyboardButton(text=post.name, callback_data=f"post_{post.id}")
                buttons.append(button)
            buttons.append(types.InlineKeyboardButton(text="↪️", callback_data='return_to_admin_menu'))
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(*buttons)
            return keyboard

    class DeleteOrEdit:
        def __get__(self, instance, owner):
            buttons = [types.InlineKeyboardButton(text='Удалить', callback_data=f"kill_{instance.message_id}"),
                       types.InlineKeyboardButton(text="Изменить",
                                                  callback_data=f'editpoststart_{instance.message_id}'),
                       types.InlineKeyboardButton(text="↪️", callback_data='return_to_admin_menu')
                       ]
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            keyboard.add(*buttons)
            return keyboard

    hello = Hello()
    proof = Proof()
    edit = Edit()
    choice = DeleteOrEdit()


async def post_menu(callback: CallbackQuery, state):
    await Admin.admin_faq_channels.set()
    await callback.answer('Успешно')
    async with state.proxy() as data:
        data['first_message'] = callback.message.message_id
    await callback.message.edit_text("Редактировать или создать новое сообщение?",
                                     reply_markup=GetKeyboard.hello)


# ------------------------------- logic of creating posts

async def create_post_start(callback: CallbackQuery):
    """step one"""
    await callback.message.edit_text(
        f"Название поста будет отображатся на кнопке управления постом в режиме изменения постов.\n"
        f"Введите название поста:")
    await Admin.admin_critical_messages_button_name.set()


async def catch_post_name(message: Message, state: FSMContext):
    """step two"""
    with Session(engine) as session:
        query = session.query(Posts).filter(Posts.name == message.text).all()
    if query:
        reply_mess = await message.reply('Такое название уже есть. Введите другое название.')
    else:
        reply_mess = await message.reply(f"Отлично, название поста сохранено. \nТеперь введите текст самого поста:")
        await Admin.admin_critical_messages_text.set()
    async with state.proxy() as data:
        data['post_name'] = message.text
        data['second_message'] = message.message_id
        data['third_message'] = reply_mess.message_id


async def catch_post_text(message: Message, state):
    """step three"""
    # await message.delete()
    async with state.proxy() as data:
        if message.caption:
            caption_text = html.escape(message.caption)
            data['caption'] = caption_text

        if message.content_type == 'photo':
            print('[INFO] photo branch ')
            photo_id = message.photo[-1].file_id
            await bot.send_photo(message.from_user.id,
                                 photo=photo_id,
                                 caption=caption_text,
                                 reply_markup=GetKeyboard.proof,
                                 parse_mode=ParseMode.HTML
                                 )


        elif message.content_type == 'document':
            print("[INFO] document branch ")
            content_document = message.document.file_id
            data['document'] = content_document


        elif message.content_type == 'video':
            print('[INFO] video branch')
            content_video = message.video.file_id
            await bot.send_video(message.from_user.id,
                                 content_video,
                                 caption=caption_text,
                                 reply_markup=GetKeyboard.proof,
                                 parse_mode=ParseMode.HTML)

            await bot.send_video(love_is,
                                 content_video,
                                 caption=caption_text,
                                 reply_markup=GetKeyboard.proof,
                                 parse_mode=ParseMode.HTML)


        elif message.content_type == 'text':
            print('[INFO] start text branch')
            data['post_text'] = message.html_text
            await bot.send_message(message.from_user.id,
                                   message.html_text,
                                   reply_markup=GetKeyboard.proof,
                                   parse_mode=ParseMode.HTML)


async def delete_messages(callback: CallbackQuery, id_1, id_2, id_3):
    await bot.delete_message(callback.message.chat.id, id_1)
    await bot.delete_message(callback.message.chat.id, id_2)
    await bot.delete_message(callback.message.chat.id, id_3)
    await callback.message.delete()


async def create_post_finally(callback: CallbackQuery, state: FSMContext):
    """last step"""
    async with state.proxy() as data:
        text = data.get('post_text')
        name = data.get('post_name')
        id_1 = data.get('first_message')
        id_2 = data.get('second_message')
        id_3 = data.get('third_message')

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Сделать заказ', url='https://t.me/ShipKZ_bot'))

    if callback.message.caption:
        caption = callback.message.caption
    else:
        caption = None

    if callback.message.text:
        print('[INFO] send text post')
        response = await bot.send_message(supported_channel, text, parse_mode=ParseMode.HTML, reply_markup=keyboard)
    elif callback.message.video:
        print('[INFO] send video post ')
        content_video = callback.message.video.file_id
        print('support channel ', supported_channel)
        print('content video ', content_video)
        print('caption ', caption)
        response = await bot.send_video(supported_channel, video=content_video, caption=caption,
                                        parse_mode=ParseMode.HTML, reply_markup=keyboard)
        print(response)
    elif callback.message.photo:
        print('[INFO] send photo post')
        response = await bot.send_photo(supported_channel, callback.message.photo, caption=caption,
                                        parse_mode=ParseMode.HTML, reply_markup=keyboard)
    else:
        await callback.message.answer('Ошибка всё плохо')
        return
    message_id = response.message_id
    await delete_messages(callback, id_1, id_2, id_3)
    add_post_to_base(message_id, supported_channel, name)
    await callback.answer(f'успешно {message_id}')
    await state.finish()
    await Admin.admin_faq_channels.set()
    await bot.send_message(callback.message.chat.id, "Доступные посты:", reply_markup=GetKeyboard.edit)


# edit posts logic ---------------------------------------------------------------------


async def edit_post_menu(callback: CallbackQuery):
    """posts menu"""
    await callback.answer('Успех')
    await callback.message.edit_text("Доступные посты:", reply_markup=GetKeyboard.edit)


async def make_choice_delete_or_edit(callback: CallbackQuery):
    print('[make_choice_delete_or_edit]')
    await callback.answer('Успех')
    data = callback.data.split("_")
    message_id: int = int(data[1])
    print(data, message_id)
    with Session(engine) as session:
        post = session.query(Posts.name).filter(Posts.id == message_id).one_or_none()
    keyboard = GetKeyboard(message_id=message_id)
    await callback.message.edit_text(post.name, reply_markup=keyboard.choice)


async def kill_post(callback: CallbackQuery):
    print('[kill post]')
    id = callback.data.split("_")[1]
    await callback.answer("успех")
    with Session(engine) as session:
        post = session.query(Posts).filter(Posts.id == id).one_or_none()
    response = delete_message(post.chat_id, post.message_id, supported_bot)
    second_message = await bot.send_message(callback.message.chat.id, str(response.status_code))
    print(response)
    with Session(engine) as session:
        stmt = delete(Posts).filter(Posts.id == id)
        session.execute(stmt)
        session.commit()
    first_message = await bot.send_message(callback.message.chat.id, 'из базы удалено')
    json_response = response.json()
    print(json_response)
    if json_response['ok'] == True:
        prefix = 'Сообщение успешно удалено в канале. '
    else:
        prefix = f"Ошибка при изменении сообщения\n" \
                 f"код ошибки {json_response['error_code']}" \
                 f"описание {json_response['description']}"

    await bot.send_message(callback.message.chat.id, f"{prefix} Доступные посты:", reply_markup=GetKeyboard.edit)
    await asyncio.sleep(2)
    await first_message.delete()
    await second_message.delete()


async def edit_post_start(callback: CallbackQuery, state: FSMContext):
    id = callback.data.split("_")[1]
    await callback.answer('Успех')
    await callback.message.delete()
    message_1 = await callback.message.answer(f'Теперь введите новый текст поста {callback.message.text}:')
    async with state.proxy() as data:
        data['id'] = id
        data['message_1_id'] = message_1.message_id
    await Admin.admin_critical_messages_newtext.set()


async def edit_post_end(message: Message, state: FSMContext):
    async with state.proxy() as data:
        id: int = data['id']
        delete_id = data['message_1_id']
    with Session(engine) as session:
        post = session.query(Posts).filter(Posts.id == id).one_or_none()
    responce = edit_message(supported_channel, post.message_id, message.html_text, supported_bot)
    responce_json = responce.json()
    print(responce_json)
    if responce_json['ok'] == True:
        text = "Сообщение успешно изменено"
    else:
        text = f"Ошибка при изменении сообщения\n" \
               f"код ошибки {responce_json['error_code']}" \
               f"описание {responce_json['description']}"
    await message.delete()
    message_1 = await bot.send_message(message.chat.id, text)
    await state.finish()
    await Admin.admin_faq_channels.set()
    await bot.send_message(message.chat.id, "Доступные посты:", reply_markup=GetKeyboard.edit)
    await asyncio.sleep(3)
    await message_1.delete()
    await bot.delete_message(message.chat.id, delete_id)


def register_handlers_critical_messages(dp: Dispatcher):
    dp.register_callback_query_handler(post_menu, lambda c: c.data in ('faq_in_channels'), state=Admin.admin)
    dp.register_callback_query_handler(create_post_start, lambda c: c.data in ('create_post'),
                                       state=Admin.admin_faq_channels)
    dp.register_message_handler(catch_post_text, content_types=types.ContentTypes.ANY,
                                        state=Admin.admin_critical_messages_text)
    dp.register_message_handler(catch_post_name, state=Admin.admin_critical_messages_button_name)
    dp.register_callback_query_handler(create_post_finally, lambda c: c.data in ('create_post_finnaly'),
                                       state=Admin.admin_critical_messages_text)
    dp.register_callback_query_handler(edit_post_menu,
                                       lambda c: c.data in ('edit_post'),
                                       state=Admin.admin_faq_channels)
    dp.register_callback_query_handler(make_choice_delete_or_edit,
                                       Regexp('post_([0-9])*'),
                                       state=Admin.admin_faq_channels)
    dp.register_callback_query_handler(kill_post, Regexp('kill_([0-9])*'), state=Admin.admin_faq_channels)
    dp.register_callback_query_handler(edit_post_start, Regexp('editpoststart_([0-9])*'),
                                       state=Admin.admin_faq_channels)
    dp.register_message_handler(edit_post_end, state=Admin.admin_critical_messages_newtext)
