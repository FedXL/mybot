import requests

from utils.config import supported_channel, supported_bot

channel = supported_channel
token = supported_bot


def get_channel_members_count(bot_token, channel_username):
    api_url = f'https://api.telegram.org/bot{bot_token}/getChatMembersCount'
    params = {
        'chat_id': channel_username
    }
    response = requests.get(api_url, params=params)
    data = response.json()
    if data['ok']:
        member_count = data['result']
        print(f"Количество пользователей в канале: {member_count}")
    else:
        print(f"Ошибка: {data['description']}")


def get_channel_members_names(bot_token, channel_username):
    api_url = f'https://api.telegram.org/bot{bot_token}/getChatMember?chat_id={channel_username}'
    response = requests.get(api_url)
    data = response.json()
    if data['ok']:
        print(data)
    else:
        print(f"Ошибка: {data['description']}")


get_channel_members_names(token, channel)


def get_channel_members_names(bot_token, channel_username):
    api_url = f'https://api.telegram.org/bot{bot_token}/getChatMembersCount'
    params = {
        'chat_id': channel_username
    }
    response = requests.get(api_url, params=params)
    data = response.json()
    if data['ok']:
        member_count = data['result']
        offset = 0
        limit = 200  # Максимальное количество пользователей, которые могут быть запрошены за один запрос
        while offset < member_count:
            api_url = f'https://api.telegram.org/bot{bot_token}/getChatMembers'
            params = {
                'chat_id': channel_username,
                'offset': offset,
                'limit': limit
            }
            response = requests.get(api_url, params=params)
            data = response.json()
            if data['ok']:
                members = data['result']
                for member in members:
                    user = member['user']
                    user_id = user['id']
                    user_first_name = user['first_name']
                    user_last_name = user.get('last_name', '')
                    print(f"ID: {user_id}, Имя: {user_first_name}, Фамилия: {user_last_name}")
                offset += limit
            else:
                print(f"Ошибка: {data['description']}")
    else:
        print(f"Ошибка: {data['description']}")


# Укажите токен вашего бота и юзернейм вашего канала
bot_token = 'YOUR_BOT_TOKEN'
channel_username = '@YOUR_CHANNEL_USERNAME'

get_channel_members_names(bot_token, channel_username)
import requests


def get_channel_members_names(bot_token, channel_username):
    api_url = f'https://api.telegram.org/bot{bot_token}/getChatMembersCount'
    params = {
        'chat_id': channel_username
    }
    response = requests.get(api_url, params=params)
    data = response.json()
    if data['ok']:
        member_count = data['result']
        offset = 0
        limit = 200  # Максимальное количество пользователей, которые могут быть запрошены за один запрос
        while offset < member_count:
            api_url = f'https://api.telegram.org/bot{bot_token}/getChatMembers'
            params = {
                'chat_id': channel_username,
                'offset': offset,
                'limit': limit
            }
            response = requests.get(api_url, params=params)
            data = response.json()
            if data['ok']:
                members = data['result']
                for member in members:
                    user = member['user']
                    user_id = user['id']
                    user_first_name = user['first_name']
                    user_last_name = user.get('last_name', '')
                    print(f"ID: {user_id}, Имя: {user_first_name}, Фамилия: {user_last_name}")
                offset += limit
            else:
                print(f"Ошибка: {data['description']}")
    else:
        print(f"Ошибка: {data['description']}")


bot_token = 'YOUR_BOT_TOKEN'
channel_username = '@YOUR_CHANNEL_USERNAME'

get_channel_members_names(bot_token, channel_username)
