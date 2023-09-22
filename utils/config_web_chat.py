import platform

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

current_os = platform.system()

if current_os == 'Windows':
    TEST_MODE = True
elif current_os == 'Linux':
    TEST_MODE = False
else:
    TEST_MODE = False

db_user = "postgres"
db_host = "localhost"
db_port = "5432"
db_password = "root"
db_name = "web_chat"

db_server_user = "postgres"
db_server_host = "localhost"
db_sever_port = "5432"
db_server_password = "12345"
db_server_name = "web_chat"



if TEST_MODE:
    DB_USER = db_user
    DB_HOST = db_host
    DB_PORT = db_port
    DB_PASS = db_password
    DB_NAME = db_name
    sharable_secret = 'secret'
    REDIS_URL = "redis://localhost"

else:
    DB_USER = db_server_user
    DB_HOST = db_server_host
    DB_PORT = db_sever_port
    DB_PASS = db_server_password
    DB_NAME = db_server_name
    sharable_secret = 'secret'
    REDIS_URL = "redis://localhost"


DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
DB_TEST= DB_URL + "_test"

async_engine_chat = create_async_engine(DB_URL, echo=False)
async_session_maker_chat = async_sessionmaker(async_engine_chat, expire_on_commit=False)
async_test_engine_chat = create_async_engine(DB_TEST, echo=False)