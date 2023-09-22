from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, BigInteger, Text, func, CheckConstraint
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import declarative_base

BaseWeb = declarative_base()




class WebMessage(BaseWeb):
    __tablename__ = 'web_messages'
    id = Column(BigInteger, primary_key=True)
    message_body = Column(String)
    is_answer = Column(Boolean)
    user = Column(BigInteger, ForeignKey('web_users.user_id'), nullable=False)
    time = Column(TIMESTAMP, server_default=func.now())
    message_type = Column(String)

    def as_dict(self):
        result = {'id': self.id,
                  'body': self.message_body,
                  'is_answer': self.is_answer,
                  'user': self.user,
                  'time': self.time.isoformat(),
                  'message_type':self.message_type}
        return result

    __table_args__ = (
        CheckConstraint(message_type.in_(['text', 'photo', 'file', 'caption']), name='check_message_type'),
    )

    def __repr__(self):
        return f"{self.id} | {self.message_body} | {self.is_answer} | {self.time}"

class WebPhoto(BaseWeb):
    __tablename__ = 'web_photos'
    id = Column(Integer, primary_key=True)
    photo_path = Column(String)
    message_id = Column(Integer,ForeignKey('web_messages.id'))

class WebUser(BaseWeb):
    __tablename__ = 'web_users'
    user_id = Column(Integer, primary_key=True)
    user_name = Column(String)
    is_kazakhstan = Column(Boolean)
    last_online = Column(TIMESTAMP)
    last_message_telegramm_id = Column(BigInteger)


class WebSocket(BaseWeb):
    __tablename__ = 'websockets'
    id = Column(BigInteger, primary_key=True)
    socket_id = Column(BigInteger)
    user_id = Column(BigInteger, ForeignKey('web_users.user_id'), unique=True)


class Jwt(BaseWeb):
    __tablename__ = 'jwt'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('web_users.user_id'), unique=True)
    jwt_hash = Column(String)
