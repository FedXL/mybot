import datetime
import time
from sqlalchemy import update, not_
from sqlalchemy.orm import Session
from base.models import OrderStatus, Order
from utils.config import engine


def main():
    while True:
        print('start new')
        three_month_ago = datetime.datetime.now() - datetime.timedelta(days=90)
        with Session(engine) as session:
            old_orders = session.query(Order.id, Order.type, OrderStatus.status, OrderStatus.order_price). \
                join(OrderStatus, Order.id == OrderStatus.order_id). \
                filter(Order.time <= three_month_ago, not_(OrderStatus.order_price.in_(['ERROR', 'Incorrect password']))).all()
            for order in old_orders:
                stmt = update(OrderStatus).filter(OrderStatus.order_id == order.id).values(status=False)
                print('tradeinn', order.id)
                session.execute(stmt)
            session.commit()
        time.sleep(60 * 60 )


if __name__ == '__main__':
    main()
