from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, BigInteger, Text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import declarative_base

from utils.config import engine

Base = declarative_base()


class Message(Base):
    __tablename__ = 'messages'
    id = Column(BigInteger, primary_key=True)
    message_body = Column(String)
    is_answer = Column(Boolean)
    time = Column(TIMESTAMP)
    storage_id = Column(BigInteger, ForeignKey('users.user_id'))


class Manager(Base):
    __tablename__ = 'managers'
    id = Column(BigInteger, primary_key=True)
    short_name = Column(String, unique=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'))
    key = Column(String, unique=True)
    is_active = Column(Boolean)


class Posts(Base):
    """Таблица постов"""
    __tablename__ = 'posts'
    id = Column(BigInteger, primary_key=True)
    message_id = Column(BigInteger)
    chat_id = Column(BigInteger)
    name = Column(String, unique=True)


    def __repr__(self):
        return f"mess: {self.message_id} | chat: {self.chat_id} | name: {self.name}"


class OrderStatus(Base):
    __tablename__ = 'order_status'
    id = Column(BigInteger, primary_key=True)
    status = Column(Boolean)
    order_id = Column(Integer, ForeignKey('orders.id'))
    manager_id = Column(BigInteger)
    order_price = Column(String, nullable=False)

    def __repr__(self):
        return f'{self.order_id} | {self.order_price} | {self.status}'


class Order(Base):
    __tablename__ = 'orders'
    id: int = Column(Integer, primary_key=True)
    client: int = Column(BigInteger, nullable=False)
    buyer = Column(BigInteger)
    time = Column(TIMESTAMP, nullable=False)
    type = Column(String, nullable=False)
    body = Column(Text, nullable=False)

    def __repr__(self):
        return f'{self.id} | {self.client} | {self.time} | {self.type}'


class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    user_name = Column(String)
    message_id = Column(Integer)
    user_second_name = Column(String)
    tele_username = Column(String)
    main_user = Column(String)
    is_kazakhstan = Column(Boolean)


class UserData(Base):
    __tablename__ = 'users_app'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(200), nullable=False)


class Discount(Base):
    __tablename__ = 'discounts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    is_vip = Column(Boolean)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)

