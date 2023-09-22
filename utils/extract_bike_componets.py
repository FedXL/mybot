import logging
import re
import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from sheets.add_orders import add_last_strings_to_basket
from utils.config import TEST_MODE
from selenium.webdriver.support import expected_conditions as EC
from utils.extract_bike_discount import Unit





class UnitComponent(Unit):
    def __init__(self, link, article, firm, unit, count, price_unit, price_total, model, img_link=None):
        super().__init__(img_link, link, article, firm, unit, count, price_unit, price_total)
        self.article = self.article.replace("Item number ", "")
        self.model = model
        self.__price_total()
        self.__unit_link()

    def __price_total(self):
        self.valuta = re.sub('\d+\.\d+|\d+', '', self.price_unit)
        self.price_total = float(re.sub("[^\d.]+", '', self.price_total))
        self.price_unit = float(re.sub('[^\d.]+', '', self.price_unit))

    def __image_link(self):
        try:
            img_link = self.img_link.split(',')[0]
            self.img_link = f'=IMAGE("{img_link}";4;40;100)'
        except Exception as ER:
            self._error = ER

    def __unit_link(self):
        link = f'=HYPERLINK("{self.link}"; "{self.article}")'
        self.link = link

    def to_tuple(self):
        return self.img_link, self.link, self.unit, self.count, self.price_unit, \
            self.price_total, self.valuta


def parce_bike_components(login_value, password_value):
    result = []
    print("[INFO] start to parce BIKE COMPONENTS")

    if TEST_MODE:
        options = Options()
        # options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        driver.maximize_window()
    elif not TEST_MODE:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--window-size=1920,1000")
        driver = webdriver.Chrome(options=options)
    driver.get("https://www.bike-components.de/en/")
    wait = WebDriverWait(driver, 20)

    wait.until(EC.visibility_of_element_located(
        (By.CLASS_NAME, "site-button-solid-icon.hidden-sm-down.accept-all-cookies.ex-accept-all-cookies"))).click()
    print('[INFO] cookies killes success')
    add_last_strings_to_basket([("Server answer:", "cookies window killed success", "try to login")], "Basket")
    time.sleep(5)
    logging.debug('[INFO] success parsing main page ... ok')
    add_last_strings_to_basket([("Server answer:", "start parce success", "try to login")], "Basket")
    time.sleep(5)

    try:
        wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, "js-login.js-site-login-link.js-account-icon.text-white"))).click()

        wait.until(EC.visibility_of_element_located(
            (By.ID, "login_email")))

        driver.find_element(By.ID, 'login_email').send_keys(login_value)
        driver.find_element(By.ID, 'login_password').send_keys(password_value)
        driver.find_element(By.ID, 'login_submit').click()

        time.sleep(4)
        add_last_strings_to_basket([("Server answer:", "login success", "try to parce basket")], "Basket")
        elements_with_basket_button = driver.find_elements(By.CLASS_NAME, "relative.block.text-white")
        for element in elements_with_basket_button:
            if element.get_attribute('title') == 'Shopping cart':
                element.click()

        print('[INFO] start to parce basket')
        wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, "items-head")))
        units = driver.find_elements(By.CLASS_NAME, "product-option-list.product-option-cart")
        print('длинна')
        print(len(units))
        for unit in units:
            unit_link = unit.find_element(By.CLASS_NAME, 'image').get_attribute('href')
            unit_name = unit.find_element(By.CLASS_NAME, "name").text
            unit_model = unit.find_element(By.CLASS_NAME, "model").text
            unit_article = unit.find_element(By.CLASS_NAME, "article-number").text
            unit_total_price = unit.find_element(By.CLASS_NAME, "price-total.col-xs-4.text-right").text
            unit_price = unit.find_element(By.CLASS_NAME, "price-single.hidden-sm-down.col-md-2.text-right").text
            count = unit.find_element(By.CLASS_NAME, "select-value").find_element(By.TAG_NAME, 'span').text
            try:
                liist = unit_price.split('\n')
                unit_price = liist[0]
            except Exception:
                print('none')

            print(unit_name, unit_total_price, unit_price, count, sep=" | ")
            result.append(
                (
                    UnitComponent(link=unit_link,
                                  article=unit_article,
                                  firm=None,
                                  unit=unit_name,
                                  count=count,
                                  price_unit=unit_price,
                                  price_total=unit_total_price,
                                  img_link="NoLink",
                                  model=unit_model).to_tuple()
                )
            )


    except Exception as ER:
        add_last_strings_to_basket([("Server answer:", "ERROR", str(ER))], "Basket")
        print("[ERROR] ", ER)
        logging.error(f"[ERROR] {ER}")
        result = [(ER)]
    finally:
        driver.quit()
        return result


def main_bc(login, psw):
    basket = parce_bike_components(login, psw)
    add_last_strings_to_basket(basket, 'Basket')


if __name__ == '__main__':
    # parce_bike_components('fedorkuruts@gmail.com','127238omgzzz' )
    main_bc('fedorkuruts@gmail.com', '127238omgzzz')
