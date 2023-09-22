import logging
import time
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from utils.config import TEST_MODE, CHROME_DRIVER_PATH


def extract_money(login_value, password_value):
    print("[INFO] start to parce money")
    logging.debug("[INFO] start to parce money")
    if TEST_MODE:
        driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH)
    else:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=options)
        driver.maximize_window()

    driver.get("https://tradeinn.com/")
    print("[INFO] getting page ... ok")
    logging.debug('[INFO] success parsing main page ... ok')
    time.sleep(3)
    try:
        language_button = driver.find_element(By.ID, "bandera_tablet")
        print('[INFO] find language_button ... ok')
        logging.debug('[INFO] find language_button ... ok')
        language_button.click()
        time.sleep(3)
        print('[INFO] click language button ... ok')
        logging.debug('[INFO] click language button ... ok')
        field_to_input = driver.find_element(By.ID, "input_buscador_paises_mob")
        field_to_input.send_keys('Russian')
        logging.debug('[INFO] find input language field language ... ok')
        time.sleep(3)
        actions = ActionChains(driver)
        actions.move_to_element(field_to_input).move_by_offset(0, 40).click().perform()
        print('[INFO] click offset 0,40 ... ok')
        logging.debug('[INFO] click 0,40 offset ... ok')
        time.sleep(4)
        print('[INFO] choice_language ... ok')
        logging.debug('[INFO] choice_language ... ok')
        button = driver.find_element(By.CLASS_NAME, "mi-cuenta-top")
        print('[INFO] find input login button ... ok')
        logging.debug('[INFO] find input login button ... ok')
        button.click()
        print('[INFO] click ... ok')
        time.sleep(4)
        login = driver.find_element(By.ID, "email_login")
        print('[INFO] find login input ... ok')
        logging.debug('[INFO] find login input ... ok')
        password = driver.find_element(By.ID, "contrasena_superior")
        print('[INFO] find password input ... ok')
        logging.debug('[INFO] find password input ... ok')
        time.sleep(2)
        login.send_keys(login_value)
        print('[INFO] password input ... ok')
        logging.debug('[INFO] password input ... ok')
        time.sleep(2)
        password.send_keys(password_value)
        print('[INFO] login input ... ok')
        logging.debug('[INFO] login input ... ok')
        time.sleep(4)
        log_in_btw = driver.find_element(By.ID, "boton_login_header")
        log_in_btw.click()
        print('[INFO] login click ... ok')
        logging.debug('[INFO] login click ... ok')
        time.sleep(4)
        try:
            is_login = driver.find_element(By.ID, "mensaje_login_header")
            if is_login:
                print('[INFO] password is not correct, stop driver ... ok')
                driver.quit()
                logging.debug("[INFO] pass is not correct ... ok ")
                return "Incorrect password"
        except Exception as Er:
            print('[INFO] you are log in ... ok')
            logging.debug(
                "[INFO] success element witch tell us that we cant to login is not found, so we are login ... ok")

        basket_btw = driver.find_element(By.CLASS_NAME, "cestatop")
        print('[INFO] find basked button ... ok')
        logging.debug('[INFO] find basked button ... ok')
        time.sleep(4)
        basket_btw.click()
        print('[INFO] busked click ... ok')
        logging.debug('[INFO] click to busked button ... ok')
        time.sleep(4)
        total = driver.find_element(By.ID, "importe_total")
        print('[INFO] find money element ... ok')
        logging.debug('[INFO] find money element ... ok')
        money = total.find_element(By.TAG_NAME, 'span').text
        logging.debug('[INFO] extract money price ... ok')
        print('[INFO]', money)
        return money
    except Exception as ER:
        print("[ERROR] ", ER)
        logging.error(f"[ERROR] {ER}")
        driver.quit()
        return f"ERROR"
    finally:
        driver.quit()


