from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
import aiogram.utils.markdown as md
from base.models import User, Discount
from create_bot import bot
from utils.config import engine
from utils.statemachine import Admin


async def init_add_dicount(callback: CallbackQuery):
    await callback.answer('Успех')
    await callback.message.answer('Для добавления клиенту скидки введите айди клиента:')
    await Admin.add_discount.set()


async def add_discount(message: Message):
    user_id = message.text
    try:
        with Session(engine) as session:
            query = session.query(User).filter(User.user_id == user_id).one_or_none()
            stmt = insert(Discount).values(is_vip=True,user_id=user_id)
            session.execute(stmt)
            session.commit()
            await message.answer(md.text(
                md.text('Скидка добавлена'),
                md.text('User name:',query.user_name ),
                md.text('User second name:',query.user_second_name),sep="\n"))
    except Exception as Error:
        await bot.send_message(message.from_user.id, Error)

def register_handlers_discounts(dp: Dispatcher):
    dp.register_callback_query_handler(init_add_dicount, lambda c: c.data in ('discounts'), state=Admin.admin)
    dp.register_message_handler(add_discount,state=Admin.add_discount)
