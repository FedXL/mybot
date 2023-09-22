import datetime
import json
from enum import Enum

from pydantic import BaseModel, Field


class Event(str, Enum):
    message = 'message'
    new_token = 'newToken'
    ask_username = 'askUsername'
    download_history = 'downloadHistory'




class MessageDetails(BaseModel):
    message_id : int
    is_answer: bool
    user_id: int
    message_type: str
    time: str = Field(default_factory=datetime.datetime.now().isoformat)
    text : str



class MessageLoad(BaseModel):
    event: Event
    name: str | None
    details: MessageDetails


data = {
    "event": "message",
    "name": None,
    "details": {"message_id": 12,
                "is_answer": True,
                "user_id": 2,
                "message_type": 'message',
                "time": datetime.datetime.now().isoformat(),
                'text': 'some text'}
}

# Десериализация JSON-строки в словарь
message = MessageLoad(**data)
print(message.event.value)
print(message.model_dump())
b = '{"event":"message","name":null,"details":{"id":12,"is_answer":true,"user":2,"message_type":"message","time":"2023-08-29T14:07:11.637746","text":"some text"}}'
c = json.loads(b)
