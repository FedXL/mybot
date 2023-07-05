from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import ParseMode, CallbackQuery
import utils.markap_menu as nv
from create_bot import bot
import aiogram.utils.markdown as md
from utils.statemachine import FAQ, OrderStates, TradeInn, BuyOut


async def started_order_handler(message: types.Message):
    if message.text == 'Сделать заказ':
        keyword_markup = types.InlineKeyboardMarkup(row_width=1)
        inline_btn = types.InlineKeyboardButton("FAQ", callback_data="FaQ")
        keyword_markup.add(inline_btn)

        await message.answer('Если возникнут трудности у нас хороший FAQ в разделе Консультаций',
                             reply_markup=keyword_markup)
        await message.answer('*Варианты доставки на Ваш выбор:*',
                             reply_markup=nv.SuperMenu.invoiceMenu,
                             parse_mode=ParseMode.MARKDOWN)


async def return_to_orders(query: CallbackQuery):
    """ Обработчик возврата к заказу из раздела FAQ"""
    income = query.data
    match income:
        case "KAZ":
            await OrderStates.order_kaz_choice.set()
            await bot.send_message(query.from_user.id,
                                   'Отлично! Теперь нам нужно получить либо доступ'
                                   ' к корзине в магазине, '
                                   'либо прямые ссылки на товары. Выбор за вами:',
                                   reply_markup=nv.SuperMenu.kaz_choice_menu)
        case "TradeInn":
            await bot.send_message(query.from_user.id,
                                   md.text(
                                       md.text("Прекрасно! Тогда понадобится логин и пароль от вашего личного "
                                               "кабинета на Tradeinn"),
                                       md.text("Введите логин: ")
                                   ),
                                   reply_markup=nv.SuperMenu.cancel
                                   )
            await TradeInn.login.set()
        case "Agent":
            await bot.send_message(query.from_user.id,
                                   md.text(
                                       md.text(
                                           "Замечательно! В таком случае нам понадобится название сайта, пароль и "
                                           "логин от личного кабинета."),
                                       md.text("Введите сайт магазина: ")
                                   ),
                                   reply_markup=nv.SuperMenu.cancel
                                   )
            await BuyOut.shop.set()


def register_handlers_othersOrder(dp: Dispatcher):
    dp.register_message_handler(started_order_handler,
                                        Text(equals="Сделать заказ"),
                                        state="*")
    dp.register_callback_query_handler(return_to_orders,
                                       lambda c: c.data in ['KAZ', "TradeInn", "Agent"],
                                       state=FAQ.start)
