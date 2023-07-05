from sqlalchemy import update
from sqlalchemy.orm import Session

from base.models import OrderStatus
from utils.config import engine

with Session(engine) as session:
    query = session.query(OrderStatus).where(OrderStatus.order_price.like('%〒%'))
    for i in query:
        print(i.id,i.order_price)
        new_price = float(i.order_price.split(" ")[0])/5.7
        rounded_value = str(round(new_price, 1)) + " " + "RUB"
        stmt = update(OrderStatus).where(OrderStatus.id == i.id).values(order_price=rounded_value)
        session.execute(stmt)
    session.commit()



