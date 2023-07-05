from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from aiogram.dispatcher import Dispatcher
from utils.config import API_TOKEN
from sqlalchemy import create_engine
from utils.config import user, host, port, database, password

# Set up logging
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)
#
# # Create a file handler for the logger
# handler = logging.FileHandler('bot.log')
# handler.setLevel(logging.DEBUG)
#
# # Add the file handler to the logger
# logger.addHandler(handler)


engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}', echo=False)

storage = MemoryStorage()
bot = Bot(API_TOKEN)
dp = Dispatcher(bot=bot,
                storage=storage)
