from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from utils.config import NAME
import utils.markap_menu as nv


async def make_first_choise_consult (message: types.Message):
    await message.answer('Koнсультация', reply_markup=nv.SuperMenu.consMenu)


# async def call_consultant (message: types.Message):
#     btn = types.InlineKeyboardButton("Консультант", url="https://t.me/Ship_KZ")
#     mini_menu = types.InlineKeyboardMarkup(row_width=1)
#     mini_menu.add(btn)
#     await message.answer(f"Нажмите кнопку ниже, чтобы вызвать консультанта.",
#                          reply_markup=mini_menu)


def register_handlers_othersCons(dp: Dispatcher):
    # dp.register_message_handler(call_consultant, Text(equals="Вызов Консультанта"), state="*"),
    dp.register_message_handler(make_first_choise_consult, Text(equals="Koнсультация"), state=None)
