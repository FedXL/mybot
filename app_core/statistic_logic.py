import datetime
from typing import List
from dateutil.relativedelta import relativedelta
from sqlalchemy import or_
from sqlalchemy.orm import Session
from base.models import Order, OrderStatus
from utils.config import engine_app


class MonthInfo:
    months = {1: 'Январь',
              2: 'Февраль',
              3: 'Март',
              4: 'Апрель',
              5: 'Май',
              6: 'Июнь',
              7: 'Июль',
              8: 'Август',
              9: 'Сентябрь',
              10: 'Октябрь',
              11: 'Ноябрь',
              12: 'Декабрь'}

    def __init__(self, data: datetime.date):
        self.nully = None
        self.zero_money = None
        self.error = None
        self.money = None
        self.error_login = None
        self.month = self.months[data.month]
        year_i = data.year
        month_i = data.month
        self.start_interval = datetime.date(year=year_i, month=month_i, day=1)
        self.end_interval = self.start_interval + relativedelta(months=1)
        self.orders = []

    def __repr__(self):
        stringi = f"{self.month:<10} | {self.start_interval} | {self.end_interval} \n"
        for i, order in enumerate(self.orders):
            stringi += str(i) + " | " + str(order) + "\n"

        return stringi

    def calculate(self):
        self.number_of_orders = len(self.orders)

    def make_report(self):
        self.error = 0
        self.money = 0
        self.error_login = 0
        self.zero_money = 0
        self.nully = 0
        for order in self.orders:
            text = order.order_price
            if text:
                if text == "Incorrect password":
                    self.error_login += 1
                elif text == 'ERROR':
                    self.error += 1
                else:
                    try:
                        money = float(order.order_price.split(" ")[0])
                        if money == 0:
                            self.zero_money += 1
                        self.money += money
                    except:
                        print(order.order_price, ' error')

            else:
                self.nully += 1


def separate_month_time_segments(now: datetime.date):
    time_start = datetime.date(year=2023, month=2, day=3)
    time_start_month = time_start.month
    result = []
    if time_start.year == now.year:
        time_end_month = now.month
        for month in range(time_start_month, time_end_month + 1):
            result.append(datetime.date(year=time_start.year, month=month, day=1, ))
    elif time_start.year < now.year:
        for month in range(time_start_month, 13):
            result.append(datetime.date(year=time_start.year, month=month, day=1))
        years = [year for year in range(time_start.year + 1, now.year, 1)]

        for year in years:
            for month in range(1, 13):
                result.append(datetime.date(year=year, month=month, day=1))

        for month in range(1, now.month + 1):
            result.append(datetime.date(year=now.year, month=month, day=1))
    return result


def create_month_info(segments):
    result = [MonthInfo(data) for data in segments]
    return result


class WeekInfo:
    pass


def get_segment_info_from_base(segments: List[MonthInfo] | List[WeekInfo]):
    with Session(engine_app) as session:
        orders = session.query(Order.time, Order.type, OrderStatus.manager_id, OrderStatus.order_price).join(
            OrderStatus, Order.id == OrderStatus.order_id).filter(Order.id >= 50, Order.type == 'TRADEINN').order_by(
            Order.id).all()

        segmentss = iter(segments)
        start_iter = next(segmentss)
        count_segment = 0
        start_interval = datetime.datetime.combine(start_iter.start_interval, datetime.time.min)
        end_interval = datetime.datetime.combine(start_iter.end_interval, datetime.time.min)
        for order in orders:
            if order.time >= end_interval:
                start_iter = next(segmentss)
                start_interval = datetime.datetime.combine(start_iter.start_interval, datetime.time.min)
                end_interval = datetime.datetime.combine(start_iter.end_interval, datetime.time.min)
                count_segment += 1
            if start_interval <= order.time < end_interval:
                segments[count_segment].orders.append(order)
    return segments


def get_segment_info_base_KZ(segments):
    with Session(engine_app) as session:
        orders = session.query(Order.time, Order.type, Order.id).filter(
            or_(Order.type == "KAZ_ORDER_LINKS", Order.type == "KAZ_ORDER_CABINET")
        ).order_by(Order.id).all()
        print('orders', orders)
        segmentss = iter(segments)
        start_iter = next(segmentss)
        count_segment = 0
        start_interval = datetime.datetime.combine(start_iter.start_interval, datetime.time.min)
        end_interval = datetime.datetime.combine(start_iter.end_interval, datetime.time.min)
        for order in orders:
            if order.time >= end_interval:
                start_iter = next(segmentss)
                start_interval = datetime.datetime.combine(start_iter.start_interval, datetime.time.min)
                end_interval = datetime.datetime.combine(start_iter.end_interval, datetime.time.min)
                count_segment += 1
            if start_interval <= order.time < end_interval:
                segments[count_segment].orders.append(order)
    return segments


def data_for_month():
    now = datetime.date.today()
    task = separate_month_time_segments(now)
    task = create_month_info(task)

    tasks = get_segment_info_from_base(task)

    for task in tasks:
        task.make_report()
    return tasks


def data_for_month_KZ():
    now = datetime.date.today()
    task = separate_month_time_segments(now)
    task = create_month_info(task)
    tasks = get_segment_info_base_KZ(task)
    return tasks

def report_month_KZ(data):

    counts = []
    for interval in data:
        counts.append([interval.month, len(interval.orders)])

    return counts


def report_month(data):
    """
    money - деньги
    counts - колличество заказов в интервал
    nullu - колличество нулевых заказов c нулевой суммой
    login_error - колличество ордеров с неверным паролем
    errors - колличество ошибок
    """
    result = {}
    money = []
    counts = []
    nullable = []
    bad_pass = []
    errors = []
    for interval in data:
        money.append([interval.month, interval.money])
        counts.append([interval.month, len(interval.orders)])
        nullable.append([interval.month, interval.zero_money])
        bad_pass.append([interval.month, interval.error_login])
        errors.append([interval.month, interval.error])

    result['money'] = money
    result['counts'] = counts
    result['zero_money'] = nullable
    result['bad_pass'] = bad_pass
    result['errors'] = errors
    return result


def main_month_report():
    data = data_for_month()
    report = report_month(data)
    data2 = data_for_month_KZ()
    report2 = report_month_KZ(data2)
    report['counts_KZ'] = report2
    for i,j in report.items():
        print(i,j)
    return report


def get_orders():
    """Получение всех заказов из бд"""
    with Session(engine_app) as session:
        tradeinn_orders = session.query(Order).filter(Order.type == 'TRADEINN', Order.id > 48).all()
        kaz_orders = session.query(Order).filter(Order.type == 'KAZ_ORDER_LINKS', Order.id > 48).all()
        kaz_cabinet = session.query(Order).filter(Order.type == 'KAZ_ORDER_CABINET', Order.id > 48).all()
        payment = session.query(Order).filter(Order.type == 'PAYMENT', Order.id > 48).all()
    result = {"Tradeinn": tradeinn_orders, "Kazakhstan cabinet": kaz_cabinet, "Kazakhstan links": kaz_orders,
              "Payment": payment}
    return result


def total_context(result):
    assert isinstance(result, dict)
    context = []
    for key, value in result.items():
        context.append([key, len(value)])
    return context


if __name__ == "__main__":
    a = data_for_month_KZ()
    for i in a:
        print(i.orders)
