import aiogram.utils.markdown as md
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ParseMode
from aiogram.utils import executor
from app_core.discount_logic import collect_discount
from base.base_catch_start_info import start_add_user_to_base
from create_bot import dp, bot
from handlers.admin.delete_manage_message import register_handlers_delete_manager_message
from handlers.admin.discount import register_handlers_discounts
from handlers.admin.faq_upload import register_handlers_upload_faq
from handlers.admin.fast_answers import register_handlers_fast_answers
from handlers.admin.posts_handler import register_handlers_critical_messages
from handlers.chat.reload_media import register_reload_media
from handlers.chat.reload_order import register_reload_order
from handlers.chat.sender import register_handlers_warning
from handlers.back_btn.btn import register_handlers_btn
from handlers.consultation.calculator import register_handlers_calculator
from handlers.consultation.faq import register_handlers_faq
from handlers.consultation.othersCons import register_handlers_othersCons
from handlers.make_an_order.othersOrder import register_handlers_othersOrder
from handlers.make_an_order.var_1 import register_handlers_var_1
from handlers.make_an_order.var_2 import register_handlers_var_2
from handlers.make_an_order.var_3 import register_handlers_var_3
from handlers.save_orders.orders_callback import register_handlers_save_order
from utils import markap_menu as nv
from utils.config import MANAGER, supported_channel
from utils.texts import make_text_hello
from utils.utils_lite import quot_replacer


async def on_startup(_):
    print("[INFO] Бот вышел в онлайн")


@dp.message_handler(chat_id=supported_channel)
async def ignore_messages(message: types.Message):
    pass



@dp.message_handler(commands=['help'], state='*')
async def help_message(message: types.Message):
    if message.from_user.id in MANAGER:
        await message.reply(md.text(
            md.text('Доступные команды:'),
            md.text('Загрузить ордер: ', '/order_', '<i>номер заказа</i>'),
            md.text('Загрузить линки: ', '/link_ <i>айди пользователя</i>'),
            md.text('Добавить/убрать из шапки: ', '/head_ <i>номер заказа</i>'),
            md.text('Загрузить фото: ', '/photo_ <i>номер фото</i>'),
            md.text('Загрузить документ ', '/doc_ <i>номер документа</i>'),
            md.text('Открыть беседу', '/talk_ <i>айди пользователя</i>'),
            sep='\n',
        ),
            parse_mode=ParseMode.HTML
        )



@dp.message_handler(commands=['discount'], state="*")
async def get_discount(message: types.Message):
    user_id = message.from_user.id
    data = collect_discount(user_id)
    await message.delete()

    await bot.send_message(message.from_user.id, md.text(
        md.text('Tradeinn накоплено: ', data['money_summary']),
        md.text('Tradeinn ваша ставка: ', data['rate'], '%'),
        md.text('Kazakhstan накоплено: ', data['kazakhstan_orders']),
        sep='\n')
    )



@dp.message_handler(commands=['start'], state="*")
async def welcome_message(message: types.Message, state: FSMContext):
    await state.finish()
    text = make_text_hello(message.from_user.first_name)
    await bot.send_message(message.from_user.id, text,
                           reply_markup=nv.SuperMenu.menu,
                           parse_mode=ParseMode.MARKDOWN)
    await start_add_user_to_base(message.from_user.id,
                                 quot_replacer(message.from_user.first_name),
                                 quot_replacer(message.from_user.last_name),
                                 quot_replacer(message.from_user.username))


@dp.message_handler(commands=['info'], state="*")
async def info_func(message: types.Message, state: FSMContext):
    await message.reply(md.text(
        md.text('chat_id:', message.chat.id),
        md.text('from_user_id:', message.from_user.id),
        md.text('from_user_name', message.from_user.first_name)
        , sep="\n"))
    value = await state.get_state()
    print("state == ", value)


def main():
    register_handlers_save_order(dp)
    register_handlers_btn(dp)
    register_handlers_othersCons(dp)
    register_handlers_othersOrder(dp)
    register_handlers_var_1(dp)
    register_handlers_var_2(dp)
    register_handlers_var_3(dp)
    register_handlers_calculator(dp)
    register_handlers_faq(dp)
    register_handlers_upload_faq(dp)
    register_handlers_critical_messages(dp)
    register_reload_media(dp)
    register_handlers_discounts(dp)
    register_reload_order(dp)
    register_handlers_fast_answers(dp)
    register_handlers_warning(dp)
    register_handlers_delete_manager_message(dp)
    executor.start_polling(dp,
                           skip_updates=True,
                           on_startup=on_startup)


if __name__ == "__main__":
    main()