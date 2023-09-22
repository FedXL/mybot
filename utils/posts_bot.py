import requests

def send_message(data, url):
    print(url)
    print(data)
    response = requests.post(url, json=data)
    response_json = response.json()
    print("[Response info]",response)
    if response.status_code == 200:
        message_id = response_json['result']['message_id']
        print("Сообщение успешно отправлено!")
    else:
        print("Ошибка при отправке сообщения. Проверьте токен и chat_id.")
        message_id = False
    return message_id

def send_photo_message(chat_id, photo, caption, bot_token):
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"

    data = {
        "chat_id": chat_id,
        "photo": photo,
        "caption": caption,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
        "reply_markup": {
            "inline_keyboard": [
                [{"text": "Сделать заказ", "url": "https://t.me/ShipKZ_bot"}]
            ]
        }
    }
    return send_message(data, url)



def send_video_message(chat_id, video, caption, bot_token):
    url = f"https://api.telegram.org/bot{bot_token}/sendVideoNote"
    print(url)
    data = {
        "chat_id": chat_id,
        "video": video,
        "caption": caption,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
        "reply_markup": {
            "inline_keyboard": [
                [{"text": "Сделать заказ", "url": "https://t.me/ShipKZ_bot"}]
            ]
        }
    }
    return send_message(data, url)



def send_message_text(chat_id, text, bot_token):
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
    return send_message(data, url)




def delete_message(chat_id, message_id, bot_token):
    url = f"https://api.telegram.org/bot{bot_token}/deleteMessage"
    data = {
        "chat_id": chat_id,
        "message_id": message_id
    }
    response = requests.post(url, json=data)
    json_response = response.json()

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


def send_fucking_photo():
    url = f"https://api.telegram.org/bot6021912534:AAEB5Pb7o38eAUmiOgVJSFApJu03BIjFzos/sendPhoto"

    data = {
        "chat_id": -1001936578982,
        "photo": 'AgACAgIAAxkBAAJFe2Sxhwfw3pCF4jYabvSs0QWJayTJAAIUzjEbLUyJSYwWajGq0Vv5AQADAgADbQADLwQ',
        "caption": 'caption',
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
    print("[Response info]", response_json)


if __name__ == "__main__":
    send_fucking_photo()