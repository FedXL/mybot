import random
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ParseMode
import utils.markap_menu as nv
import aiogram.utils.markdown as md
from create_bot import bot
from utils.statemachine import TradeInn
import html

"""----------------------------ЗАКАЗ ЧЕРЕЗ traideINN---------------------------------------------------------"""


async def start_tradeinn(message: types.Message):
    await message.answer("Прекрасно! Тогда понадобится логин и пароль от вашего личного кабинета на Tradeinn")
    await TradeInn.login.set()
    await message.answer('Введите логин: ', reply_markup=nv.SuperMenu.cancel)


async def switch_from_faq(query: types.CallbackQuery):
    await bot.send_message(query.from_user.id,"Прекрасно! Тогда понадобится логин и пароль от вашего личного кабинета на Tradeinn")
    await TradeInn.login.set()
    await bot.send_message(query.from_user.id,
                           'Введите логин: ',
                           reply_markup=nv.SuperMenu.cancel)


async def get_tradeinn_login(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        encoded_text = html.escape(message.text)
        data['login'] = encoded_text
    await message.answer("Ваш логин сохранен!")
    await message.answer("Введите пароль", reply_markup=nv.SuperMenu.cancel)
    await TradeInn.pas.set()


async def get_tradeinn_pass(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        encoded_text = html.escape(message.text)
        data['pass'] = encoded_text
    mini_menu = types.InlineKeyboardMarkup(row_width=1)
    btn = types.InlineKeyboardButton("Подтвердить заказ", callback_data="TRADEINN")
    mini_menu.add(btn)
    await message.answer(md.text(
        md.text("Если всё правилно подтвердите заказ:"),
        md.text("Вариант 2.", "Заказ через TradeInn",sep="\n"),
        md.text('Логин: ', f"<b>{data.get('login')}</b>"),
        md.text("Пaроль: ", f"<b>{data.get('pass')}</b>"),
        sep='\n'),
        parse_mode=ParseMode.HTML,
        reply_markup=mini_menu)


def register_handlers_var_2(dp: Dispatcher):
    dp.register_message_handler(start_tradeinn, Text(equals='Заказ Tradeinn'), state=None)
    dp.register_message_handler(get_tradeinn_login, state=TradeInn.login)
    dp.register_message_handler(get_tradeinn_pass, state=TradeInn.pas)
    dp.register_callback_query_handler(switch_from_faq, text="TadeInn")

