import requests

def send_message(chat_id, text, bot_token):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
        "reply_markup": {
            "inline_keyboard": [
                [{"text": "Сделать заказ", "url": "https://t.me/ShipKZ_bot"}]
            ]
        }
    }
    response = requests.post(url, json=data)
    response_json = response.json()
    message_id = response_json['result']['message_id']

    if response.status_code == 200:
        print("Сообщение успешно отправлено!")
    else:
        print("Ошибка при отправке сообщения. Проверьте токен и chat_id.")
    return message_id


def delete_message(chat_id,message_id,bot_token):
    url = f"https://api.telegram.org/bot{bot_token}/deleteMessage"
    data = {
        "chat_id": chat_id,
        "message_id": message_id
    }
    response = requests.post(url, json=data)
    json_response=response.json()

    if response.status_code == 200:
        print("Удалено")
    else:
        print("Ошибка при удалении. Проверьте токен, chat_id и message_id.")
    return response


def edit_message(chat_id, message_id, new_text, bot_token):
    url = f"https://api.telegram.org/bot{bot_token}/editMessageText"
    data = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": new_text,
        "disable_web_page_preview": True,
        "reply_markup": {
            "inline_keyboard": [
                [{"text": "Сделать заказ", "url": "https://t.me/ShipKZ_bot"}]
            ]
        },
        "parse_mode": "HTML"
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        print("Сообщение успешно изменено!")
    else:
        print("Ошибка при изменении сообщения. Проверьте токен, chat_id и message_id.")
    return response


def foo():
    from config import TOKEN_BOT_HANDLER, test_group
    text = 'hello'
    send_message(test_group, text, TOKEN_BOT_HANDLER)


def foo2(message_id):
    from config import TOKEN_BOT_HANDLER
    text = "❤️❤️❤️"
    from utils.config import supported_channel
    edit_message(supported_channel, message_id, text, TOKEN_BOT_HANDLER)

