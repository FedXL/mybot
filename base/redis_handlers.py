import redis

# Подключение к серверу Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)
redis_client.pubsub()

def send_redis_mess_to_web(message):
    channel = 'news'
    data = str(message)
    redis_client.publish(channel, data)

