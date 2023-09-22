from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.types import ParseMode, Message, CallbackQuery
from create_bot import bot
import aiogram.utils.markdown as md
from utils.statemachine import FAQ
from utils.texts import make_text_for_FAQ
import utils.markap_menu as nv
from utils.exchange import get_exchange_lockal


async def hello_faq(message: Message):
    await bot.send_message(message.from_user.id, md.text(
        md.text("Добро пожаловать в наш ", md.bold('FAQ'), "!"),
        md.text('По каждому из способов доставки мы имеем исчерпывающее руководство.'),
        md.text('Какой способ доставки вас интересует?'),
        sep='\n'),
                           reply_markup=nv.SuperMenu.faqMenu,
                           parse_mode=ParseMode.MARKDOWN)
    await FAQ.start.set()


async def generate_faq(message: Message):
    mini_menu = types.InlineKeyboardMarkup(row_width=1)
    money_rate = get_exchange_lockal()
    eur = money_rate.eur
    usd = money_rate.usd


    if message.text == "Покупка транзитом через Казахстан":
        btn = types.InlineKeyboardButton("Cделать заказ", callback_data="KAZ")
        mini_menu.add(btn)
        await message.answer(make_text_for_FAQ('faq_1'),
                             reply_markup=mini_menu,
                             disable_web_page_preview=True,
                             parse_mode=ParseMode.HTML
                             )

    elif message.text == "Покупка на Tradeinn":
        btn = types.InlineKeyboardButton("Cделать заказ", callback_data="TradeInn")
        mini_menu.add(btn)
        await message.answer(make_text_for_FAQ('faq_2'),
                             parse_mode=ParseMode.HTML,
                             disable_web_page_preview=True,
                             reply_markup=mini_menu
                             )


    elif message.text == "Покупка через почтовых посредников":
        btn = types.InlineKeyboardButton("Cделать заказ", callback_data="Agent")
        mini_menu.add(btn)
        await message.answer(make_text_for_FAQ('faq_3'),
                             parse_mode=ParseMode.HTML,
                             disable_web_page_preview=True,
                             reply_markup=mini_menu,
                             )
    else:
        await message.reply("Я такой команды не знаю! Используйте меню для выбора ответа.",
                            reply_markup=nv.SuperMenu.faqMenu)


async def return_to_faq(query: CallbackQuery):
    await query.answer("FAQ")
    await bot.send_message(query.from_user.id, md.text(
        md.text("Добро пожаловать в наш ", md.bold('FAQ'), "!"),
        md.text('По каждому из способов доставки мы имеем исчерпывающее руководство.'),
        md.text('Какой способ доставки вас интересует?'),
        sep='\n'),
                           reply_markup=nv.SuperMenu.faqMenu,
                           parse_mode=ParseMode.MARKDOWN)
    await FAQ.start.set()


def register_handlers_faq(dp: Dispatcher):
    dp.register_message_handler(hello_faq, Text(equals='FAQ'), state=None)
    dp.register_message_handler(generate_faq, state=FAQ.start)
    dp.register_callback_query_handler(return_to_faq, lambda c: c.data == 'FaQ')
