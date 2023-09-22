from typing import Dict, List, Tuple

from sqlalchemy import Row, cast, ARRAY, Integer, update, delete, not_
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql._typing import _TP

from base.models import User, Order, OrderStatus, Message
from utils.config import engine_app, engine


class OrderAndPrice:
    def __init__(self):
        from base.models import Order, OrderStatus, User
        with Session(engine) as session:
            users = session.query(User).all()
            self.users = users
            self.orders = session.query(Order, OrderStatus).join(OrderStatus, Order.id == OrderStatus.order_id).all()
        self.data_kz = self.get_kz_users_with_orders()
        self.data = self.get_tradeinn_users_with_orders()
        self.data = self.add_summ_orders_to_data()

    def get_total_users(self):
        return len(self.users)

    def get_active_users(self):
        """users had orders"""
        orders = self.orders
        user_id = set()
        for order in orders:
            user_id.add(order.Order.client)
        return len(user_id)

    def get_active_tradeinn_users(self):
        user_id_tradeinn = set()
        for order in self.orders:
            if order.Order.type == 'TRADEINN':
                user_id_tradeinn.add(order.Order.client)
        return user_id_tradeinn

    def get_tradeinn_users_with_orders(self):
        data = {}
        for order in self.orders:
            if order.Order.type == 'TRADEINN':
                user_info = data.get(order.Order.client)
                if user_info:
                    user_info['orders'][order.Order.id] = order.OrderStatus.order_price
                else:
                    data[order.Order.client] = {'orders': {order.Order.id: order.OrderStatus.order_price}}
        return data

    def get_kz_users_with_orders(self):
        data = {}
        for order in self.orders:
            if order.Order.type in ["KAZ_ORDER_CABINET", 'KAZ_ORDER_LINKS']:
                user_info = data.get(order.Order.client)
                if user_info:
                    user_info['orders'][order.Order.id] = order.OrderStatus.order_price
                else:
                    data[order.Order.client] = {'orders': {order.Order.id: order.OrderStatus.order_price}}
        return data

    def add_summ_orders_to_data(self):
        data = self.data
        for user, user_orders in data.items():
            orders = user_orders['orders']
            money_sum = 0
            for order_id, order_price in orders.items():
                try:
                    string = order_price.split(' ')
                    money = float(string[0])
                    money_sum += money
                except:
                    pass
            orders['money_sum'] = int(money_sum)
            data[user] = orders
        return data


class Discounts(OrderAndPrice):
    def __init__(self):
        super().__init__()

    def __separate_users_d(self, first: int, second: int):
        data = self.data
        first_step = '0' + "-" + str(int(first / 1000))
        second_step = str(int(first / 1000)) + "-" + str(int(second / 1000))
        last_step = str(int(second / 1000)) + "+"
        new_data = {first_step: {},
                    second_step: {},
                    last_step: {}}
        for user, orders in data.items():
            if orders['money_sum'] < first:
                user_orders = new_data[first_step]
                user_orders[user] = orders
                new_data[first_step] = user_orders
            elif first <= orders['money_sum'] < second:
                user_orders = new_data[second_step]
                user_orders[user] = orders
                new_data[second_step] = user_orders
            elif second <= orders['money_sum']:
                user_orders = new_data[last_step]
                user_orders[user] = orders
                new_data[last_step] = user_orders
        return new_data

    def get_discounts_diagram_data(self, first, second):
        data = self.__separate_users_d(first=first, second=second)
        result = []
        for key, values in data.items():
            result.append([key, len(values)])
        return result

    def get_discout_users(self, first, second):
        data = self.__separate_users_d(first=first, second=second)
        return data


class UserProfit(OrderAndPrice):
    def __init__(self):
        super().__init__()
        self.data = self.__separate_users()

    def __separate_users(self) -> Dict[int, Dict[str, List[str]]]:
        """{money_key:{'users':['user_id_1,user_id_2 ...]}"""
        result = {a: {'users': []} for a in range(0, 205, 5)}

        for user, orders in self.data.items():
            money = orders['money_sum']
            money_key = (money // 5000) * 5000
            if money_key >= 200000:
                money_key = 200000
            money_key = int(money_key / 1000)
            user_list = result[money_key]['users']
            user_list.append(user)
        return dict(reversed(result.items()))

    def get_bar_diogramm(self) -> list[list[int]]:
        total = []
        for key, value in self.data.items():
            try:
                total.append([key, len(value['users'])])
            except:
                pass
        return total

    def get_users_by_money_lvl(self, money_lvl):
        assert money_lvl % 5 == 0
        assert money_lvl <= 200
        data = self.data.get(money_lvl)
        with Session(engine) as session:
            users = data.get('users')
            users_info = session.query(User).filter(User.user_id.in_(users)).all()
        return users_info


class UserInfo:
    def __init__(self, user_id: int | bool | List):
        if user_id:
            self.user_id = user_id
            self.data = self.__get_user_by_id()
        else:
            self.data = self.__get_all_users_info()

    def __get_user_by_id(self):
        user_id = self.user_id
        result = {'user': None, 'orders': None}
        with Session(engine) as session:
            orders = session.query(Order, OrderStatus).join(OrderStatus, Order.id == OrderStatus.order_id).filter(
                Order.client == user_id).order_by(Order.id).all()
            user = session.query(User).filter(User.user_id == user_id).one_or_none()
            result['user'] = user
            result['orders'] = orders
        return result

    def __get_all_users_info(self) -> list[Row[_TP]]:
        with Session(engine) as session:
            result = session.query(Order, OrderStatus, User).join(OrderStatus, Order.id == OrderStatus.order_id).join(
                User, Order.client == User.user_id).all()
        return result


class OrderInfo:
    def __init__(self, order_id):
        self.order_id = order_id
        self.data = self.__get_order_by_id()

    def __get_order_by_id(self):
        with Session(engine) as session:
            order = session.query(Order, OrderStatus). \
                join(OrderStatus, Order.id == OrderStatus.order_id). \
                filter(Order.id == self.order_id). \
                one_or_none()

            messages = session.query(Message).filter(Message.storage_id == order.Order.client).order_by(
                Message.id).all()
        data = {'order': order, 'messages': messages}
        return data


class GetMessages:
    def __init__(self):
        Session = sessionmaker(bind=engine)
        self.__session = Session()

    def get_messages_by_id(self, user_id):
        messages = self.__session.query(Message).filter(Message.storage_id == user_id).order_by(Message.id).all()
        self.__session.close()
        return messages


def change_order(order_id, order_type, order_price, order_manager):
    try:
        with Session(engine) as session:
            stmt = update(Order).where(Order.id == order_id).values(type=order_type)
            stmt2 = update(OrderStatus).where(OrderStatus.order_id == order_id).values(order_price=order_price,
                                                                                       manager_id=order_manager)
            session.execute(stmt)
            session.execute(stmt2)
            session.commit()
        return True
    except Exception as ER:
        return False


def kill_order(order_id: int):
    try:
        with Session(engine) as session:
            stmt = delete(OrderStatus).where(OrderStatus.order_id == order_id)
            stmt2 = delete(Order).where(Order.id == order_id)
            session.execute(stmt)
            session.execute(stmt2)
            session.commit()
            return True
    except Exception as ER:
        print(ER)
        return False


class GetUsers:
    def __init__(self):
        Session = sessionmaker(bind=engine)
        self.__session = Session()

    def sort_by_id(self):
        query = self.__session.query(User).order_by(User.user_id).all()
        self.__session.close()
        return query

    def sort_by_name(self):
        query = self.__session.query(User).order_by(User.user_name).all()
        self.__session.close()
        return query

    def sort_by_second_name(self):
        query = self.__session.query(User).order_by(User.user_second_name).all()
        self.__session.close()
        return query

    def sort_by_username(self):
        query = self.__session.query(User).order_by(User.tele_username).all()
        self.__session.close()
        return query


class GetOrders:
    def __init__(self):
        Session = sessionmaker(bind=engine)
        self.__session = Session()

    def get_orders(self):
        orders = self.__session.query(Order.id,
                                      Order.client,
                                      Order.type,
                                      Order.time,
                                      OrderStatus.order_price,
                                      OrderStatus.manager_id). \
            join(OrderStatus, Order.id == OrderStatus.order_id). \
            order_by(Order.id).all()
        self.__session.close()
        return orders


def get_all_users():
    with Session(engine) as session:
        query = session.query(User).order_by(User.user_name)


class DiscountsKZ(OrderAndPrice):
    """cubes_data = {number of orders : {user_id:{orders:{order_id: money}},user_id2....}"""

    def __init__(self):
        super().__init__()
        self.cubes_data = self.__create_cubes_data()
        self.cubes_data = dict(sorted(self.cubes_data.items()))
        # self.cubes_count_data = self.__create_count_user_orders_set()

    def __create_cubes_data(self):
        # {number of orders : {user_id:{orders:{order_id: money}},user_id2....}
        finaly_data = {}
        for user, info in self.data_kz.items():
            key = len(info['orders'])

            is_key = finaly_data.get(key)
            if is_key:
                is_key[user] = info
            else:
                finaly_data[key] = {user: info}
        return finaly_data

    def get_users_by_lvl(self, lvl):
        data = self.cubes_data.get(lvl)
        if data:
            with Session(engine) as session:
                users = data.keys()
                users_info = session.query(User).filter(User.user_id.in_(users)).all()
            return users_info
        else:
            return False


def collect_discount(client_id: int):
    """функция для получения информации о накопленых скидках"""

    with Session(engine) as session:

        query = session.query(Order, OrderStatus).filter(Order.id == OrderStatus.order_id, Order.client == client_id)
        tradeinn_orders = query.filter(Order.type == "TRADEINN").all()
        kazakhstan_orders = query.filter(not_(Order.type.in_(["TRADEINN"]))).all()
        print(tradeinn_orders)
        print(kazakhstan_orders)

        summ = 0
        lose = ['Incorrect password', None, 'Не вышло залогиниться', 'ERROR', 'Не вышло.']
        for order in tradeinn_orders:
            price = order.OrderStatus.order_price
            if price not in lose:
                summ += float(price.split(' ')[0])
        summ = int(summ)
        if summ < 100000:
            discount = 10
        elif 100000 <= summ < 200000:
            discount = 8
        elif summ >= 200000:
            discount = 7

        result = {'client': client_id,
                  'money_summary': summ,
                  'rate': discount,
                  'kazakhstan_orders': len(kazakhstan_orders)}
        return result


if __name__ == '__main__':
    print(collect_discount(463025329))
