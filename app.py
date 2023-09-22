import json
import datetime
from flask import Flask, jsonify, render_template, request, redirect, url_for
from sqlalchemy import update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash

from app_core.discount_logic import OrderAndPrice, Discounts, UserProfit, UserInfo, OrderInfo, change_order, kill_order, \
    GetUsers, GetOrders, GetMessages, DiscountsKZ
from app_core.statistic_logic import main_month_report, get_orders, total_context
from base.models import Order, Manager, OrderStatus, UserData
from loop_extract_money import ParceTask
from sheets.add_orders import add_last_strings_to_basket
from utils.config import flask_port, flask_host, MANAGER_TRADEINN, TEST_MODE
from sqlalchemy.sql import text
from flask_login import LoginManager, login_user, login_required
from utils.config import engine_app

app = Flask(__name__)
app.config['TIMEOUT'] = 60
app.config['SECRET_KEY'] = 'my-super-secret: 9807uafda;f3!;ld0Dzcsdc_)#*$*#!@e.;./zFEAFAs'

login_manager = LoginManager()
login_manager.init_app(app)
app.permanent_session_lifetime = datetime.timedelta(days=1)


class UserLogin:
    def from_db(self, user_id):
        self.__user = get_user_by_id(user_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.__user.id)


@login_manager.user_loader
def load_user(user_id):
    return UserLogin().from_db(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    return redirect('/login')


@app.route('/')
@login_required
def start_page():
    context = create_context()
    return render_template('start_page.html', context=context)


def create_context():
    order_query = get_orders()
    total_result = total_context(order_query)
    month_statistic = main_month_report()
    context = {'total_result': total_result,
               'month_money': month_statistic['money'],
               'month_count': month_statistic['counts'],
               'month_zero_money': month_statistic['zero_money'],
               'month_bad_pass': month_statistic['bad_pass'],
               'month_errors': month_statistic['errors'],
               'month_cont_KZ': month_statistic['counts_KZ']}

    return context


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = get_user_by_login(request.form['username'])
        if user and check_password_hash(user.password, request.form['password']):
            user_login = UserLogin().create(user)
            login_user(user_login)
            return redirect(url_for('start_page'))
        else:
            print("else")
            return "Mistake"
    return render_template('login.html')


def get_user_by_login(login):
    with Session(engine_app) as session:
        user = session.query(UserData).filter(UserData.username == login).one_or_none()
        if user:
            return user
        else:
            return False


def get_user_by_id(user_id: int):
    with Session(engine_app) as session:
        user = session.query(UserData).filter(UserData.id == user_id).one()
        if user:
            return user
        else:
            return False


def sql_suffer(string: str):
    keywords = ['update', 'delete', 'drop', 'table', 'database']
    string_lower = string.lower()
    for word in keywords:
        if word in string_lower:
            print('sql attack')
            raise TypeError
    return string


def add_message_to_base(user_id, message_id, message_text):
    with Session(engine_app) as session:
        query = text(
            "INSERT INTO messages (message_body, is_answer, storage_id, time, message_id) VALUES (:message_body, "
            ":is_answer, :storage_id, now(), :message_fake_id)")
        session.execute(query, {"message_body": message_text, "is_answer": True, "storage_id": user_id,
                                "message_fake_id": message_id})
        session.commit()


@app.route('/managers')
@login_required
def get_manager_panel():
    managers = tuple(MANAGER_TRADEINN.keys())

    with Session(engine_app) as session:
        query = session.query(Manager).filter(Manager.user_id.in_(managers), Manager.key.isnot(None)).all()
    context = query
    return render_template("managers.html", context=context)


@app.route('/manager<int:id>/<string:turn>')
@login_required
def manager_handler(id: int, turn):
    turn = turn

    if turn == 'TurnOff':
        action = False
    elif turn == 'TurnOn':
        action = True
    else:
        return "ERROR"

    with Session(engine_app) as session:
        stmt = update(Manager).where(Manager.user_id == id).values(is_active=action)
        session.execute(stmt)
        session.commit()
    return redirect(url_for('get_manager_panel'))


def make_check(manager: int, key):
    with Session(engine_app) as session:
        query = session.query(Manager.is_active, Manager.key).filter(Manager.user_id == manager).one_or_none()

    if query.is_active and query.key == key:
        return True
    else:
        return False


@app.route('/api/orders', methods=['POST'])
def extract_order_info():
    data = request.get_json()
    manager: int = data['manager']
    key = data['key']
    check = make_check(manager, key)
    if not check:
        result = [{'answer': False}]
        return json.dumps(result)
    with Session(engine_app) as session:
        query_manager = session.query(Manager).filter(Manager.user_id == manager).one_or_none()
        current_date = datetime.datetime.now()
        twenty_four_hours_ago = current_date - datetime.timedelta(hours=24)
        # Строим запрос
        orders = session.query(Order.id, Order.body, OrderStatus.manager_id). \
            join(OrderStatus, Order.id == OrderStatus.order_id). \
            filter(Order.time >= twenty_four_hours_ago, Order.type == "TRADEINN", OrderStatus.manager_id == manager). \
            all()
        orders_lt = []
        result = [{'answer': True,
                   'orders': orders_lt}]
        for order in orders:
            orders_lt.append({
                "order_id": order.id,
                "body": order.body,
                "manager_id": order.manager_id
            })
        json_result = json.dumps(result)
    return json_result


@app.route('/api/basket', methods=['POST'])
def parce_basket():
    print("start_basket")
    data = request.get_json()
    login = data['login']
    psw = data['psw']
    shop = data['shop']
    string = login + " | " + psw + " | " + shop
    add_last_strings_to_basket([("Server answer:", "parce task", string)], "Basket")
    with Session(engine_app) as session:
        if shop == "bike-discount":
            query = insert(ParceTask).values(login=login,
                                             password=psw,
                                             type='BASKET_BD')
            session.execute(query)
            session.commit()
        elif shop == "bike-components":
            query = insert(ParceTask).values(login=login,
                                             password=psw,
                                             type='BASKET_BC')
            session.execute(query)
            session.commit()
        else:
            result = {"answer": "fail"}
            return json.dumps(result)
    result = {
        "answer": "success",
    }
    return json.dumps(result)


@app.route('/api/receive-data', methods=['POST'])
def receive_data():
    data = request.get_json()
    print("[INFO] receive_data: ", data)
    try:
        user_id = data['user_id']
        text_from_data = '[Sheets] ' + data['text']
        user_id = sql_suffer(user_id)
        text_safe = sql_suffer(text_from_data)
        message_id = 11111
        add_message_to_base(user_id, message_id, text_safe)
        print("[INFO] данные успешно сохранены")
    except Exception as ER:
        print("[ERROR]", ER)
        return jsonify({'message': 'fail'})
    return jsonify({'message': 'Data received successfully'})


@app.route('/parsing')
@login_required
def get_parsing_panel():
    return f"<br><a href='{url_for('start_page')}'> Пока не готово. </a>"


@app.route('/discounts')
@login_required
def get_discount_panel():
    data = {'data': UserProfit().data,
            'discount_pie': Discounts().get_discounts_diagram_data(50000, 100000),
            'data_kz': DiscountsKZ().cubes_data}

    return render_template('cubes.html', context=data)


@app.route('/discounts/pie', methods=["POST"])
@login_required
def get_pie_data():
    """some logic"""
    if request.method == 'POST':
        data = request.get_json()
        lvl1 = int(data.get('lvl_1'))
        lvl2 = int(data.get('lvl_2'))
        discount_pie = Discounts().get_discounts_diagram_data(lvl1 * 1000, lvl2 * 1000)

    return discount_pie


@app.route('/users/<int:money_spended_lvl>', methods=["GET"])
@login_required
def users_info(money_spended_lvl):
    """получить пользователей по уровню денег"""
    users_info = UserProfit().get_users_by_money_lvl(money_spended_lvl)
    lvl =f"{money_spended_lvl} - {money_spended_lvl + 5}"
    if money_spended_lvl >=200:
        lvl = "200+"
    return render_template('users.html', context=users_info , remark = f"Уровень трат на Tradeinn {lvl} т.р.")

@app.route('/users_kz/<int:count_of_orders>',methods=["GET"])
@login_required
def users_info_kz(count_of_orders):
    data = DiscountsKZ().get_users_by_lvl(count_of_orders)
    if data:
        return render_template('users.html', context=data , remark = f"Колличество заказов через Казахстан: {count_of_orders} ")
    else:
        return {'error': 'нету с таким уровнем пользователей'}


@app.route('/users/<string:sorted_by>', methods=["GET"])
@login_required
def users_info_all(sorted_by):
    users = GetUsers()
    if sorted_by == 'id':
        data = users.sort_by_id()
    elif sorted_by == 'name':
        data = users.sort_by_name()
    elif sorted_by == 'second_name':
        data = users.sort_by_second_name()
    elif sorted_by == "username":
        data = users.sort_by_username()
    else:
        return {'success':False,'error':f"sorted_by = {sorted_by} not in [id,name,second_name,username]"}
    return render_template('users.html', context = data)


@app.route('/user/<int:user>', methods=['GET'])
@login_required
def user_info(user):
    if request.method == 'GET':
        user_id: int = user
        print("[INFO] received_data:", user_id)
        if user_id:
            context = UserInfo(user_id).data
            messagetext = GetMessages().get_messages_by_id(user_id)
            print(messagetext)
            return render_template('user.html', context=context, context2=messagetext)


@app.route('/order/<int:order>', methods=['GET'])
@login_required
def get_order_panel(order):
    data = OrderInfo(order_id=order).data
    return render_template('order.html', context=data)

@app.route('/order/delete', methods=['POST'])
@login_required
def delete_order():
    print('[info] start delete order')
    if request.method == "POST":
        data = request.form.to_dict()
        id = int(data.get('order_id'))
        result=kill_order(id)
        return {'success': result}

@app.route('/base', methods=['GET'])
@login_required
def get_base_():
    #тестовая функция для базового шаблона
    print('start')

    return render_template('base.html')

@app.route('/order', methods=["GET"])
@login_required
def orders_info():
    data = GetOrders().get_orders()
    return render_template('orders.html',context = data)

@app.route('/order/edit', methods=['POST'])
@login_required
def edit_order():
    if request.method == "POST":
        data = request.form.to_dict()

        order_type = data.get('order_type')
        order_money = data.get('order_price')
        order_manager = data.get('manager_id')
        order_type_before = data.get('order_type_before')
        order_money_before = data.get('order_money_before')
        order_manager_before = data.get('manager_id_before')
        if order_type == order_type_before and order_money == "" and order_manager == "":
            return {'mistake': "no changes detected"}
        elif order_type == order_type_before and order_money == order_money_before and order_manager == order_manager_before:
            return {'mistake': "no changes detected"}
        else:
            if order_manager == "":
                order_manager = order_manager_before
            if order_money == "":
                order_money = order_money_before
            if order_manager == 'null':
                order_manager == order_manager_before
            if order_manager == 'null':
                order_manager = None
            result = change_order(order_id=data.get('order_id'), order_type=order_type, order_price=order_money,
                                  order_manager=order_manager)
            if result:
                return {'result': 'success'}
            else:
                return {'result': 'fail'}


if __name__ == '__main__':
    app.run(host=flask_host, port=flask_port, debug=TEST_MODE)
