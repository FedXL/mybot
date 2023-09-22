import html

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ParseMode
import utils.markap_menu as nv
import aiogram.utils.markdown as md
from utils.statemachine import BuyOut

"""-------------------------------------ВЫКУП ЗАКАЗА-------------------------------------------------------"""


async def start_buyout(message: types.Message):
    await message.answer("Замечательно! В таком случае нам понадобятся: "
                         "Название сайта , пароль и логин от личного кабинета.")
    await message.answer('Введите сайт магазина:', reply_markup=nv.SuperMenu.cancel)
    await BuyOut.shop.set()


async def get_buyout_shop(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        encoded_text = html.escape(message.text)
        data['shop'] = encoded_text
    await message.answer('Сайт успешно сохранён.')
    await message.answer('Введите логин: ', reply_markup=nv.SuperMenu.cancel)
    await BuyOut.login.set()


async def get_buyout_login(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        encoded_text = html.escape(message.text)
        data['login'] = encoded_text
    await message.answer('Логин успешно сохранён!')
    await message.answer('Введите пароль:', reply_markup=nv.SuperMenu.cancel)
    await BuyOut.pas.set()


async def get_buyout_pass(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        encoded_text = html.escape(message.text)
        data['pass'] = encoded_text
    await message.answer('Если всё правильно, подтвердите заказ.', reply_markup=nv.SuperMenu.cancel)
    mini_menu = types.InlineKeyboardMarkup(row_width=1)
    btn = types.InlineKeyboardButton("Подтвердить заказ", callback_data="PAYMENT")
    mini_menu.add(btn)
    await message.answer(md.text(
        md.text("Вариант 3."),
        md.text("Выкуп через посредника"),
        md.text('Магазин: ', f"<b>{data.get('shop')}</b>"),
        md.text('Логин:', f"<b>{data.get('login')}</b>"),
        md.text('Пароль: ', f"<b>{data.get('pass')}</b>"),
        sep='\n'),
        reply_markup=mini_menu,
        parse_mode=ParseMode.HTML)


def register_handlers_var_3(dp: Dispatcher):
    dp.register_message_handler(start_buyout, Text(equals='Выкуп заказа'), state=None)
    dp.register_message_handler(get_buyout_shop, state=BuyOut.shop)
    dp.register_message_handler(get_buyout_login, state=BuyOut.login)
    dp.register_message_handler(get_buyout_pass, state=BuyOut.pas)
