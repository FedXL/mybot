import time
import requests
from sqlalchemy import ForeignKey, select, delete, text
from sqlalchemy import String, Integer
from sqlalchemy.orm import Session, declarative_base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from utils.extract_bike_componets import main_bc
from utils.extract_bike_discount import main_bd
from utils.extract_price import extract_money
from utils.config import API_TOKEN, alerts, engine
import logging


logger = logging.getLogger()

# Создание обработчика для консольного вывода
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
logger.addHandler(console_handler)

# Создание обработчика для записи в файл
file_handler = logging.FileHandler('logs/parce.log', encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
logger.addHandler(file_handler)

# Установка уровня логирования на DEBUG
logger.setLevel(logging.DEBUG)
Base = declarative_base()


class ParceTask(Base):
    __tablename__ = 'parce_task'
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey('orders.id'), nullable=True)
    login: Mapped[str] = mapped_column(String)
    password: Mapped[str] = mapped_column(String)
    type: Mapped[str] = mapped_column(String)



def tradinn_money_extract(login, password, order_id, session):
    money = extract_money(login, password)
    stmt2 = text("UPDATE order_status SET order_price = :money WHERE order_id = :order_id")
    session.execute(stmt2, {"money": money, "order_id": order_id})
    session.commit()
    url = "https://api.telegram.org/bot" + API_TOKEN + "/sendMessage?chat_id=" + str(
        alerts) + "&text=" + str(order_id) + " | " + str(money)
    response = requests.get(url)
    return response


def money_loop2():
    logger.info('Start parce task loop .. ok')
    logger.debug('Debug lvl start parce')
    with Session(engine) as session:
        while True:
            logger.debug('start new iteration')
            query = select(ParceTask.id,ParceTask.order_id, ParceTask.login, ParceTask.password, ParceTask.type)
            parce_tasks = session.execute(query).fetchall()
            if len(parce_tasks) != 0:
                logger.info('We have task to parce')
                for task in parce_tasks:
                    login = task.login
                    psw = task.password
                    try:
                        match task.type:
                            case 'TRADEINN':
                                logger.info('We have TRADEINN parce task')
                                order_id = task.order_id
                                response = tradinn_money_extract(login, psw, order_id, session)
                                logger.info(response)
                            case 'BASKET_BD':
                                logger.info('We have Bike Discount parce task')
                                main_bd(login, psw)
                            case 'BASKET_BC':
                                logger.info('We have Bike Components parce task')
                                main_bc(login, psw)
                    except Exception as ER:
                        logger.error(ER)
                        print('[error]', ER)
                    stmt = delete(ParceTask).where(ParceTask.id == task.id)
                    session.execute(stmt)
                    session.commit()
                logger.debug('IM STEEL HERE')
            time.sleep(5)

def money_loop1():
    logger.info('Start parce task loop .. ok')
    logger.debug('Debug lvl start parce')

    while True:
        with Session(engine) as session:
            logger.debug('start new iteration')
            query = select(ParceTask.id,ParceTask.order_id, ParceTask.login, ParceTask.password, ParceTask.type)
            parce_tasks = session.execute(query).fetchall()
            if len(parce_tasks) != 0:
                logger.info('We have task to parce')
                for task in parce_tasks:
                    login = task.login
                    psw = task.password
                    try:
                        match task.type:
                            case 'TRADEINN':
                                logger.info('We have TRADEINN parce task')
                                order_id = task.order_id
                                response = tradinn_money_extract(login, psw, order_id, session)
                                logger.info(response)
                            case 'BASKET_BD':
                                logger.info('We have Bike Discount parce task')
                                main_bd(login, psw)
                            case 'BASKET_BC':
                                logger.info('We have Bike Components parce task')
                                main_bc(login, psw)
                    except Exception as ER:
                        logger.error(ER)
                        print('[error]',ER)
                    stmt = delete(ParceTask).where(ParceTask.id == task.id)
                    session.execute(stmt)
                    session.commit()
                logger.debug('IM STEEL HERE')
            time.sleep(5)





if __name__ == "__main__":
    money_loop2()
