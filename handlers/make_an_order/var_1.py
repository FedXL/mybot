import html

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ParseMode
import utils.markap_menu as nv
from utils.statemachine import OrderStates
from create_bot import bot
import aiogram.utils.markdown as md
from utils.texts import make_links_info_text, get_vaflalist, get_additional_from_proxi
from utils.utils_lite import ShopValid, create_new_message_order


"""______________________Сделать заказ через Казахстан_________________________________"""

async def order_kaz_start_handler(message: types.Message):
    print("Start order_kaz_start_handler")
    await OrderStates.order_kaz_choice.set()
    await message.answer('Отлично! Теперь нам нужно получить либо доступ'
                         ' к корзине в магазине, '
                         'либо прямые ссылки на товары. Выбор за вами:',
                         reply_markup=nv.SuperMenu.kaz_choice_menu)


async def make_order_kaz_choice(message: types.Message, state: FSMContext):
    print("[INFO] make_order_kaz_choice")
    if message.text == "Предоставлю доступ в личный кабинет":
        async with state.proxy() as data:
            data['kaz_choice'] = 'href'
            print("data" * 100, data, sep="\n")
        await message.answer('Принято! Тогда нам понадобится название'
                             ' магазина, логин и пароль для'
                             ' доступа в личный кабинет и корзине с товарами.')
        await message.answer('Введите название магазина:', reply_markup=nv.SuperMenu.cancel)
        await OrderStates.order_kaz_ch1_shop_name.set()
    elif message.text == "Предоставлю ссылки на товары":
        async with state.proxy() as data:
            data['kaz_choice'] = 'bascet'
            print("data" * 100, data, sep="\n")
        await message.answer(f"Принято! В таком случае нам понадобится:\n"
                             f"Название магазина. \n"
                             f"Прямые ссылки на каждый из желаемых"
                             f" товаров c коментариями.\nP.S. ссылка должна быть ПРЯМОЙ, а не из корзины магазина.")
        await message.answer('Введите название магазина:', reply_markup=nv.SuperMenu.cancel)
        await OrderStates.order_kaz_ch2_shop_name.set()
    else:
        await message.reply('Непонятная команда, используйте кнопки меню для ответа')


# ----------------------------------------------------------------------------------------------------------------------
# Shop choice handlers

async def get_shop_name(message: types.Message, state):
    valid = ShopValid(message.text)
    if not valid:
        await message.reply("что-то пошло не так, не похоже на название магазина попробуйте еще раз:")
    else:
        async with state.proxy() as data:
            encoded_text = html.escape(message.text)
            data['shop'] = encoded_text
        await message.answer("Имя магазина успешно сохранено!")
        await message.answer("Введите логин для доступа в личный кабинет:", reply_markup=nv.SuperMenu.cancel)
        await OrderStates.order_kaz_ch1_loggin.set()


async def get_login(message: types.Message, state):
    if len(message.text) > 75:
        await message.reply(f"Логин длинный какой то \n"
                            f"на спам похоже. Попробуйте ещё")
    else:
        async with state.proxy() as data:
            encoded_text = html.escape(message.text)
            data['log'] = encoded_text
        await message.answer("Логин успешно сохранён!")
        await message.answer("Введите пароль для доступа в личный кабинет:", reply_markup=nv.SuperMenu.cancel)
        await OrderStates.order_kaz_ch1_password.set()


async def get_password(message: types.Message, state):
    order_type = "KAZ_ORDER_CABINET"
    if len(message.text) > 75:
        await message.reply(f" Пароль длинный какойто \n"
                            f" на спам похоже. Попробуйте ещё")
    else:
        async with state.proxy() as data:
            encoded_text = html.escape(message.text)
            data['pass'] = encoded_text
        await message.answer("Пароль успешно сохранён!")
        mini_menu = types.InlineKeyboardMarkup(row_width=1)
        btn = types.InlineKeyboardButton("Подтвердить заказ", callback_data=order_type)
        mini_menu.add(btn)
        await message.answer("Если всё правильно, подтвердите заказ.", reply_markup=nv.SuperMenu.cancel)
        await bot.send_message(message.chat.id,
                               md.text(
                                   md.text("Вариант 1", 'Заказ через казахстан', sep="\n"),
                                   md.text('Магазин: ', f"<b>{data.get('shop')}</b>"),
                                   md.text('Логин:', f"<b>{data.get('log')}</b>"),
                                   md.text('Пароль: ', f"<b>{data.get('pass')}</b>"),
                                   sep='\n'),
                               reply_markup=mini_menu,
                               parse_mode=ParseMode.HTML,
                               )


# ----------------------------------------------------------------------------------------------------------------------
# links choice handlers:


async def get_shop_name_links(message: types.Message, state):
    valid = ShopValid(message.text)
    if not valid:
        await message.reply("что-то пошло не так, не похоже на название магазина попробуйте еще раз:")
    else:
        async with state.proxy() as data:
            encoded_text = html.escape(message.text)
            data['shop'] = encoded_text
        await message.reply("Имя магазина успешно сохранено!")
        await message.answer("Введите первую ссылку:", reply_markup=nv.SuperMenu.cancel)
        await OrderStates.order_kaz_ch2_href.set()

def clean_href(text):
    """иногда когда клиенты копируют ссылки на товары перед Https идет еще префикс магазина . Тут я пытаюсь от него избавится"""
    try:
        result = text.split('https:')
        result = 'https:' + result[1]
    except:
        result = text
    return result

async def get_href(message: types.Message, state: FSMContext):
    print("[INFO] get_href start")
    vaflalist = get_vaflalist(1)
    href_text = clean_href(message.text)
    href_text = html.escape(href_text)
    async with state.proxy() as data:
        num = data.get('num')
        print("data" * 100, data, sep="\n")
        if num is None:
            data['href_1'] = href_text
            data['num'] = 1
            await message.reply(f'Ваша первая ссылка сохранена')
            await message.answer(f"Добавьте комментарий ,если нужно или завершите заказ. \n"
                                 f"(количество, цвет, размер , всё что считаете необходимым)",
                                 reply_markup=nv.SuperMenu.CommentMenu)
        elif num is not None:
            num = int(num)
            if num <= 14:
                num += 1
                data['num'] = num
                hrefs = 'href_' + str(num)
                data[hrefs] = href_text
                await message.reply(f'Ваша {vaflalist[num - 1]} ссылка сохранена')
                await message.answer(f'Добавьте комментарий или завершите заказ:',
                                     reply_markup=nv.SuperMenu.CommentMenu)
            elif num > 14:
                await message.reply(f'Ваша шестнадцатая ссылка ссылка не сохранена. '
                                    f'Обнаружено превышение здравого смысла. '
                                    f'Лучше передайте контроль над личным кабинетом '
                                    f'Или оформите ещё один заказ.',
                                    reply_markup=nv.SuperMenu.CommentMenu)
        await OrderStates.order_kaz_ch2_comment.set()


async def get_comment(message: types.Message, state: FSMContext):
    vaflalist = get_vaflalist(2)
    await OrderStates.order_kaz_ch2_href.set()
    async with state.proxy() as data:
        num = data.get('num')
        if num is None:
            encoded_text = html.escape(message.text)
            data['comment_1'] = encoded_text
            data['num'] = 1
            await message.answer(f'Ваша первая ссылка сохранена')
            await message.answer('Введите ссылку на следующий товар или завершите заказ:',
                                 reply_markup=nv.SuperMenu.kaz_order)
        elif num is not None:
            num = int(num)
            if num <= 14:
                data['num'] = num
                comment = 'comment_' + str(num)
                encoded_text = html.escape(message.text)
                data[comment] = encoded_text
                await message.answer(f'Ваш комментарий к {vaflalist[num - 1]} ссылке сохранен')
                await message.answer(f'Введите ссылку на следующий товар или завершите заказ:',
                                     reply_markup=nv.SuperMenu.kaz_order)
        print("[INFO] get_comment")
        print("data" * 100, data, sep="\n")
            # elif num > 14:
            #     await message.answer(f'Ваша шестнадцатая ссылка ссылка не сохранена. '
            #                          f'Обнаружено превышение здравого смысла. '
            #                          f'Лучше передайте контроль над личным кабинетом '
            #                          f'Или оформите ещё один заказ.',
            #                          reply_markup=nv.SuperMenu.kaz_order)
    await OrderStates.order_kaz_ch2_href.set()


async def end_hrefs(message: types.Message, state: FSMContext):
    texts = [f"Вариант 1.",
             f"Заказ через Казахстан."]
    async with state.proxy() as data:
        addition = get_additional_from_proxi(data)
        await message.answer("Если всё правильно, подтвердите заказ.", reply_markup=nv.SuperMenu.cancel)
        mini_menu = types.InlineKeyboardMarkup(row_width=1)
        btn = types.InlineKeyboardButton("Подтвердить заказ", callback_data="KAZ_ORDER_LINKS")
        mini_menu.add(btn)
        await message.answer(md.text(*texts, *addition, sep="\n"),
                             reply_markup=mini_menu,
                             disable_web_page_preview=True,
                             parse_mode=ParseMode.HTML
                             )
        print('[INFO] end_hrefs')


def register_handlers_var_1(dp: Dispatcher):
    # выбор:
    dp.register_message_handler(order_kaz_start_handler, Text(equals="Заказ через Казахстан"), state=None)
    dp.register_message_handler(make_order_kaz_choice, state=OrderStates.order_kaz_choice)
    # магазин:
    dp.register_message_handler(get_shop_name, state=OrderStates.order_kaz_ch1_shop_name)
    dp.register_message_handler(get_login, state=OrderStates.order_kaz_ch1_loggin)
    dp.register_message_handler(get_password, state=OrderStates.order_kaz_ch1_password)
    # ссылки:
    dp.register_message_handler(get_shop_name_links, state=OrderStates.order_kaz_ch2_shop_name)
    dp.register_message_handler(end_hrefs, Text(equals='Завершить заказ'),
                                state=[OrderStates.order_kaz_ch2_href, OrderStates.order_kaz_ch2_comment])

    dp.register_message_handler(get_href, state=OrderStates.order_kaz_ch2_href)
    dp.register_message_handler(get_comment, state=OrderStates.order_kaz_ch2_comment)
