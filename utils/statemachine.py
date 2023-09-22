from aiogram.dispatcher.filters.state import StatesGroup, State


class OrderStates(StatesGroup):
    order_kaz_choice = State()
    order_kaz_ch1_shop_name = State()
    order_kaz_ch1_loggin = State()
    order_kaz_ch1_password = State()
    order_kaz_ch2_shop_name = State()
    order_kaz_ch2_href = State()
    order_kaz_ch2_comment = State()
    menu = State()
    advice = State()


class TradeInn(StatesGroup):
    login = State()
    pas = State()


class BuyOut(StatesGroup):
    shop = State()
    login = State()
    pas = State()


class FAQ(StatesGroup):
    start = State()


class Calculator_1(StatesGroup):
    euro_usd = State()
    get_money = State()
    result = State()


class Calculator_2(StatesGroup):
    euro_usd = State()
    get_money = State()
    result = State()


class Admin(StatesGroup):
    admin = State()
    admin_faq_channels = State()
    admin_critical_messages_button_name=State()
    admin_critical_messages_text=State()
    admin_critical_messages_newtext=State()

    faq_refactoring = State()

    answers = State()
    change_button = State()
    change_answer = State()

    delete_manager_message = State()

    add_discount = State()

class Chat(StatesGroup):
    first = State()
    second = State()
