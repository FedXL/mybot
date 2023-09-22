import asyncio
import datetime
import time

from sqlalchemy import insert
from sqlalchemy.orm import Session

from app_core.discount_logic import Discounts
from base.models import Message
from create_bot import bot
from aiogram.types import ParseMode

from utils.config import engine
from utils.texts import make_no_discount_text, make_discount_text


async def send_discount(user, text):
    await bot.get_session()
    result = await bot.send_message(user, text, parse_mode=ParseMode.HTML)
    session = await bot.get_session()
    await session.close()
    print(result)
    return result


def safe_message(session: Session(), data):
    print('start')
    message_id = data.message_id
    user_id = data.chat.id
    text = data.text
    time = datetime.datetime.now()
    stmt = insert(Message).values(message_body=text,
                                  is_answer=True,
                                  storage_id=user_id,
                                  time=time,
                                  message_id=message_id)
    session.execute(stmt)
    session.commit()


async def main():
    data = Discounts().get_discout_users(100000, 200000)
    percent_10 = data['0-100']
    percent_8 = data['100-200']
    percent_7 = data['200+']
    with Session(engine) as session:
        for user, info in percent_10.items():
            await asyncio.sleep(1)
            money_summ = info['money_sum']
            money_summ = money_summ // 1000
            text = make_no_discount_text(money_summ)
            try:
                result = await send_discount(user, text)
                safe_message(session=session, data=result)
            except Exception as ER:
                print("FUCKING ERROR")
                print(ER)
        for user, info in percent_8.items():
            await asyncio.sleep(1)
            text = make_discount_text(8)
            try:
                result = await send_discount(user, text)
                safe_message(session=session, data=result)
            except Exception as ER:
                print("FUCKING ERROR")
                print(ER)

        for user, info in percent_7.items():
            await asyncio.sleep(1)
            text = make_discount_text(7)
            try:
                result = await send_discount(user, text)
                safe_message(session=session, data=result)
            except Exception as ER:
                print(ER)


if __name__ == "__main__":
    asyncio.run(main())
