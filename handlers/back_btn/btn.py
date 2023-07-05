from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
import utils.markap_menu as nv
from create_bot import dp
from utils.statemachine import OrderStates


@dp.message_handler(Text(equals="Назад"), state="*")
async def back_btn_function(message: types.Message, state: FSMContext):
    value = await state.get_state()
    match value:
        case "TradeInn:login":
            await state.finish()
            await message.answer("Вы вернулись назад в меню заказа",
                                 reply_markup=nv.SuperMenu.invoiceMenu)

        case "TradeInn:pas":
            await state.finish()
            await message.answer("Вы вернулись назад в меню заказа",
                                 reply_markup=nv.SuperMenu.invoiceMenu)

        case "BuyOut:shop":
            await state.finish()
            await message.answer('Вы вернулись назад в меню заказа!',
                                 reply_markup=nv.SuperMenu.invoiceMenu)

        case "BuyOut:login":
            await state.finish()
            await message.answer('Вы вернулись назад в меню заказа!',
                                 reply_markup=nv.SuperMenu.invoiceMenu)

        case "OrderStates:order_kaz_choice":
            await state.finish()
            await message.answer("Меню выбора заказа",
                                 reply_markup=nv.SuperMenu.invoiceMenu)

        case "OrderStates:order_kaz_ch1_shop_name":
            await state.finish()
            await OrderStates.order_kaz_choice.set()
            await message.answer('Вы вернулись назад! Теперь нам нужно получить либо доступ'
                                 ' к корзине в магазине, '
                                 'либо предоставить прямые ссылки на товары. Выбор за вами:',
                                 reply_markup=nv.SuperMenu.kaz_choice_menu)

        case "OrderStates:order_kaz_ch2_href":
            await state.finish()
            await OrderStates.order_kaz_choice.set()
            await message.answer('Вы вернулись назад! Теперь нам нужно получить либо доступ'
                                 ' к корзине в магазине, '
                                 'либо прямые ссылки на товары. Выбор за вами:',
                                 reply_markup=nv.SuperMenu.kaz_choice_menu)

        case "OrderStates:order_kaz_ch2_comment":
            await state.finish()
            await OrderStates.order_kaz_choice.set()
            await message.answer('Вы вернулись назад! Теперь нам нужно получить либо доступ'
                                 ' к корзине в магазине, '
                                 'либо прямые ссылки на товары. Выбор за вами:',
                                 reply_markup=nv.SuperMenu.kaz_choice_menu)

        case "OrderStates:order_kaz_ch2_shop_name":
            await state.finish()
            await OrderStates.order_kaz_choice.set()
            await message.answer('Вы вернулись назад! Теперь нам нужно получить либо доступ'
                                 ' к корзине в магазине, '
                                 'либо прямые ссылки на товары. Выбор за вами:',
                                 reply_markup=nv.SuperMenu.kaz_choice_menu)

        case "OrderStates:order_kaz_ch1_loggin":
            await state.finish()
            await OrderStates.order_kaz_choice.set()
            await message.answer('Вы вернулись назад! Теперь нам нужно получить либо доступ'
                                 ' к корзине в магазине, '
                                 'либо прямые ссылки на товары. Выбор за вами:',
                                 reply_markup=nv.SuperMenu.kaz_choice_menu)

        case "OrderStates:order_kaz_ch1_password":
            await state.finish()
            await OrderStates.order_kaz_choice.set()
            await message.answer('Вы вернулись назад! Теперь нам нужно получить либо доступ'
                                 ' к корзине в магазине, '
                                 'либо прямые ссылки на товары. Выбор за вами:',
                                 reply_markup=nv.SuperMenu.kaz_choice_menu)

        case "FAQ:start":
            await state.finish()
            await message.answer('Вы вернулись назад в меню консультаций!',
                                 reply_markup=nv.SuperMenu.consMenu)

        case "Calculator_1:euro_usd":
            await state.finish()
            await message.answer("Вы вернулись в меню консультаций.",
                                 reply_markup=nv.SuperMenu.consMenu)

        case "Calculator_1:get_money":
            await state.finish()
            await message.answer("Вы вернулись в меню консультаций.",
                                 reply_markup=nv.SuperMenu.consMenu)

        case "Calculator_2:euro_usd":
            await state.finish()
            await message.answer("Вы вернулись в меню консультаций.",
                                 reply_markup=nv.SuperMenu.consMenu)

        case "Calculator_2:get_money":
            await state.finish()
            await message.answer("Вы вернулись в меню консультаций.",
                                 reply_markup=nv.SuperMenu.consMenu)
        case "BuyOut:pas":
            await state.finish()
            await message.answer("Меню выбора заказа",
                                 reply_markup=nv.SuperMenu.invoiceMenu)

        case None:
            await message.answer('Вы вернулись в главное меню',
                                 reply_markup=nv.SuperMenu.menu)


def register_handlers_btn(dp: Dispatcher):
    dp.register_message_handler(back_btn_function, Text(equals="Назад"), state="*")
