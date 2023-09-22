import datetime

from sqlalchemy import update, select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from base.chat_models import WebMessage, WebPhoto
from base.models import Message, Photo, Document


async def add_photo_to_db_(session: AsyncSession, user_id_: int, photo_id: int, prefix: str,
                           is_answer: bool, message_id: int = None):

    if message_id:
        new_message = Message(is_answer=is_answer,
                              storage_id=user_id_,
                              message_id=message_id,
                              time=datetime.datetime.now())
    else:
        new_message = Message(is_answer=is_answer, storage_id=user_id_)
    session.add(new_message)
    await session.flush()
    message_id_in_db: int = new_message.id
    session.add(Photo(file_id=photo_id, message_id=message_id_in_db))
    text = prefix + str(message_id_in_db)
    await session.execute(update(Message).where(Message.id == message_id_in_db).values(message_body=text))
    await session.flush()
    return text


async def add_document_to_db_(session: AsyncSession,
                              prefix: str,
                              is_answer: bool,
                              user_id: int,
                              message_id: int,
                              document_id: str
                              ):
    time = datetime.datetime.now()
    new_message = Message(is_answer=is_answer,
                          storage_id=user_id,
                          message_id=message_id,
                          time=time)
    session.add(new_message)
    await session.flush()
    message_id_in_db: int = new_message.id
    new_doc = Document(document_id=document_id, message_id=message_id_in_db)
    session.add(new_doc)
    text = prefix + str(message_id_in_db)
    await session.execute(update(Message).where(Message.id == message_id_in_db).values(message_body=text))
    await session.flush()


async def save_text_message_to_db(text: str, user_web_id: int, is_answer: bool,
                                  session: AsyncSession,message_type='text')->int:

    message = WebMessage(message_body=text,
                           is_answer=is_answer,
                           user=user_web_id,
                         message_type=message_type)
    session.add(message)
    await session.flush()
    id = message.id
    return id


async def get_messages_from_base_last_5_g(user_id: int, session: AsyncSession):
    stmt = select(Message.is_answer, Message.message_body).where(Message.storage_id == user_id).order_by(
        desc(Message.id)).limit(5)
    result = await session.execute(stmt)
    rows = result.fetchall()
    return rows


async def get_messages_from_web_db(user_id: int, session: AsyncSession):
    stmt = select(WebMessage.is_answer, WebMessage.message_body).where(WebMessage.user == user_id).order_by(
        desc(WebMessage.id)).limit(5)
    result = await session.execute(stmt)
    rows = result.fetchall()
    return rows


async def save_photo_message_to_web_db(photo_path: str,photo_command, user_id: int, is_answer: bool, session: AsyncSession ):

    new_message = WebMessage(message_body=photo_command,
                           is_answer=is_answer,
                           user=user_id,
                           message_type='photo')
    session.add(new_message)
    await session.flush()
    message_id = new_message.id
    photo = WebPhoto(photo_path=photo_path,
                         message_id=message_id)
    session.add(photo)
    await session.flush()
    photo_id = photo.id
    return message_id