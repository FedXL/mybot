import re
import time
from selenium.webdriver.support import expected_conditions as EC
from typing import List
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium import webdriver
import requests
from selenium.webdriver.support.wait import WebDriverWait
from manager_config import manager, KEY


class Order:
    def __init__(self, order):
        self.order = order['order_id']
        self.login = self.extract_login(order['body'])
        self.psw = self.extract_password(order['body'])

    @staticmethod
    def extract_login(order_body):
        string = order_body
        match = re.search("<code>(.*?)</code>", string)
        if match:
            login = match.group(1)
            return login
        else:
            print("Логин не найден.")
            raise Exception('Не далось извлечь логин')

    @staticmethod
    def extract_password(order_body):
        string = order_body
        match = re.search("<code>(.*?)</code>[^<]*<code>(.*?)</code>", string)
        if match:
            password = match.group(2)
            return password
        else:
            print("Пароль не найден.")
            raise Exception('Не удалось извлечь пароль')

    def __repr__(self):
        return f"{self.order} | {self.login} | {self.psw}"


def send_request(manager):
    key = KEY
    url = "http://188.130.160.216:6969/api/orders"

    data = {"manager": manager,
            "key": key}
    response = requests.post(url, json=data).json()

    if response[0]['answer'] == True and len(response[0]['orders']) != 0:
        print('[INFO] response ... ok')
    elif response[0]['answer'] == True and len(response[0]['orders']) == 0:
        print('Доступа к заказам у вас нет')
        print('Закрепите заказ в меню заказа телеграм бота или обратитесь к администратору')
        print('Приложение закроется через 30 секунд:')
        for i in (range(30, 1, -1)):
            print(i)
            time.sleep(1)
        raise Exception('boom')
    elif response[0]['answer'] == False:
        print("Не удалось пройти авторизацию. Вы отключены, либо пользуетесь устаревшей версией скрипта.")
        for i in (range(30, 1, -1)):
            print(i)
            time.sleep(1)
        raise Exception('boom')

    return response


def parce_response(request: List[dict]) -> List[Order]:
    orders = {}
    request = request[0]['orders']
    for order in request:
        orders[order["order_id"]] = (Order(order))
    return orders


def main():
    response = send_request(manager=manager)
    orders: {int: Order} = parce_response(response)
    if len(orders) > 1:
        print("Доступные номера заказов заказов:", *orders.keys())
        order_number = int(input("Выберите номер заказа из доступных: "))
        if order_number not in orders.keys():
            print(f'Ошибка ввода для вас доступны заказы: {orders.keys()}')
            print('Приложение закроется через 10 секунд:')
            for i in (range(10, 1, -1)):
                print(i)
                time.sleep(1)
            raise Exception('boom')
        go_to_cabinet(orders[order_number].login, orders[order_number].psw)
    else:
        for i in orders.values():
            info: Order = i
            print('[INFO] order: ', info.order)
            go_to_cabinet(info.login, info.psw)


def go_to_cabinet(login_value, password_value):
    print("[INFO] start script")
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)
    driver.get("https://tradeinn.com/")
    print("[INFO] parce tradeinn.com ... ok")
    time.sleep(3)
    try:
        # language_button = driver.find_element(By.ID, "bandera_tablet")
        # print(language_button)
        # print('[INFO] language_button ... ok')
        # language_button.click()
        # a = input('a')
        # wait.until(EC.visibility_of_element_located((By.ID, "input_buscador_paises_mob")))
        # field_to_input = driver.find_element(By.ID, "input_buscador_paises_mob")
        # field_to_input.send_keys('Russian')
        # time.sleep(1)
        # actions = ActionChains(driver)
        # actions.move_to_element(field_to_input).move_by_offset(0, 40).click().perform()
        # print('[INFO] click ... ok !')
        #
        # time.sleep(3)
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "mi-cuenta-top"))).click()
        #
        # print('[INFO] choice_language ... ok')
        # a = input('a')
        wait.until(EC.visibility_of_element_located((By.ID, "email_login")))
        login = driver.find_element(By.ID, "email_login")
        print('[INFO] login ... ok')
        password = driver.find_element(By.ID, "contrasena_superior")
        print('[INFO] password ... ok')
        login.send_keys(login_value)
        time.sleep(0.3)
        print('[INFO] password input ... ok')
        password.send_keys(password_value)
        time.sleep(0.3)
        print('[INFO] login input ... ok')
        log_in_btw = driver.find_element(By.ID, "boton_login_header")
        log_in_btw.click()
        print('[INFO] log into account ... ok')
        time.sleep(4)
        try:
            is_login = driver.find_element(By.ID, "mensaje_login_header")
            if is_login:
                return "Не вышло залогиниться"
        except Exception:
            print('[INFO] you are in ... ok')
        # wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "icocarrito.icocarrito_d"))).click()
        driver.execute_script("alert('manager script v 1.02:\\nВход завершён, можно работать.\\nНе забудь отключить систему автоматизированного "
                              "управления Chrome!\\n!!!Надо на крестик ткнуть!!! \\n"
                              "При оплате paypal, сначала авторизация по номеру "
                              "телефона потом по паролю.');")
        print('[INFO] you can work, you have 2 hours')
        for i in range(1, 120):
            print(f"[INFO] time left: {(120 - i)//60} hours {(120-i) % 60} minutes")
            time.sleep(60)
        print('Bye! Bye!')
        time.sleep(60)
    except Exception as ER:
        print("[ERROR] ", ER)
        time.sleep(20)
    finally:
        driver.quit()


if __name__ == "__main__":
    print(manager)
    main()
