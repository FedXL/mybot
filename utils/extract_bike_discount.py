import logging
import time
from telnetlib import EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sheets.add_orders import add_last_strings_to_basket
from utils.config import TEST_MODE
from selenium.webdriver.support import expected_conditions as EC


class Unit:
    def __init__(self, img_link, link, article, firm, unit, count, price_unit, price_total):
        self.img_link = img_link
        self.link = link
        self.firm = firm
        self.unit = unit
        self.count = count
        self.price_unit = price_unit
        self.price_total = price_total
        self.article = article

    def __repr__(self):
        return f"{self.article} | link | photo | {self.firm} | {self.unit} | {self.count} | {self.price_unit} | {self.price_total}"


class UnitDiscount(Unit):
    def __init__(self, img_link, link, article, firm, unit, count, price_unit, price_total):
        super().__init__(img_link, link, article, firm, unit, count, price_unit, price_total)
        self.article = self.article.replace("Item no. ", "")
        self.__price_total()
        self.__image_link()
        self.__unit_link()
        self.__unit()

    def __price_total(self):
        self.valuta = self.price_unit.split(' ')[1]
        self.price_total = float(self.price_total.split(" ")[0].replace(',','.'))
        self.price_unit = float(self.price_unit.split(" ")[0].replace(',','.'))

    def __image_link(self):
        try:
            img_link = self.img_link.split(',')[0]
            self.img_link = f'=IMAGE("{img_link}";4;40;100)'
        except Exception as ER:
            self._error = ER

    def __unit_link(self):
        link = f'=HYPERLINK("{self.link}"; "{self.article}")'
        self.link = link

    def __unit(self):
        self.unit = self.firm + " | " + self.unit

    def to_tuple(self):
        return self.img_link, self.link, self.unit, self.count, self.price_unit, \
            self.price_total, self.valuta


def parce_bike_discount(login_value, password_value):
    result = []
    print("[INFO] start to parce BIKE DISCOUNT")
    if TEST_MODE:
        driver = webdriver.Chrome()
        driver.maximize_window()
    elif not TEST_MODE:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--window-size=1920,1000")
        driver = webdriver.Chrome(options=options)
    driver.get("https://www.bike-discount.de/en/account")
    print('[INFO] preparing ... ok')
    wait = WebDriverWait(driver, 20)
    driver.execute_script("window.scrollBy(0, 300);")
    driver.save_screenshot('/root/utils/sc1.png')
    time.sleep(1)
    print('[INFO] scroll ... ok')
    print("[INFO] scroll 5 times ... ok")
    logging.debug('[INFO] success parsing main page ... ok')
    driver.save_screenshot('/root/utils/sc2.png')
    print("[INFO] kill fucking cookes or smth ")
    add_last_strings_to_basket([("Server answer:", "start parce success", "try to login")], "Basket")
    try:
        inpute_login_field = driver.find_element(By.ID, "email")
        inpute_pass_field = driver.find_element(By.ID, "passwort")
        inpute_login_field.send_keys(login_value)
        inpute_pass_field.send_keys(password_value)

        button = driver.find_element(By.CLASS_NAME, 'register--login-btn.btn.is--primary.is--large.is--icon-right')
        driver.save_screenshot('/root/utils/sc3.png')
        button.click()
        print('[INFO] loggin button punsh .. ok')
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "navigation--entry.entry--service.has--drop-down.delivery"))).click()


        wait.until(EC.visibility_of_element_located(
            (By.CLASS_NAME, "service--entry.flag-icon-kz.entry77.service--link"))).click()
        print('[INFO] kz delivery ... ok')
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "btn.is--icon-left.cart--link"))).click()
        print('[INFO] punsh to cart ... ok')
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "btn.button--open-basket.is--icon-right"))).click()
        print('[INFO] enter to basket ... ok')
        add_last_strings_to_basket([("Server answer:", "login success", "try to parce basket")], "Basket")
        driver.save_screenshot('/root/utils/sc5.png')
        units = wait.until(
            EC.visibility_of_all_elements_located((By.CLASS_NAME, "table--tr.block-group.row--product")))
        for unit in units:
            print('#++++++')
            img = unit.find_element(By.TAG_NAME, 'img')
            img = img.get_attribute('srcset')
            link = unit.find_element(By.CLASS_NAME, 'content--title')
            href = link.get_attribute('href')
            name_of_item = link.get_attribute('title')
            name_of_firm = link.find_element(By.TAG_NAME, 'strong').text
            id = unit.find_element(By.CLASS_NAME, "content--sku.content").text
            quantity = unit.find_element(By.NAME, "sQuantity").find_elements(By.TAG_NAME, 'option')
            for option in quantity:
                a = option.get_attribute('selected')
                if a is not None:
                    num = option.text
                    break
                else:
                    num = 'mistake'
            price = unit.find_element(By.CLASS_NAME, "panel--td.column--total-price.is--align-right").text
            price_unit = unit.find_element(By.CLASS_NAME, "panel--td.column--unit-price.is--align-right").text
            print(price_unit)
            print(price)
            result.append(
                (
                    UnitDiscount(
                        img_link=img,
                        link=href,
                        firm=name_of_firm,
                        unit=name_of_item,
                        count=num,
                        article=id,
                        price_unit=price_unit,
                        price_total=price
                    ).to_tuple()
                )
            )

    except Exception as ER:
        add_last_strings_to_basket([("Server answer:", "ERROR", str(ER))], "Basket")
        print("[ERROR] ", ER)
        logging.error(f"[ERROR] {ER}")
        return [(ER)]

    finally:
        driver.quit()
        return result


def main_bd(login,psw):
    basket=parce_bike_discount(login,psw)
    add_last_strings_to_basket(basket,"Basket")


if __name__ == '__main__':
    main_bd('fedorkuruts@gmail.com','127238omgzzz')