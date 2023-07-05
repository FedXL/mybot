import os
from bs4 import BeautifulSoup
from selenium import webdriver
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from base.base_connectors import insert_to_base
from base.base_handlers_bot import save_exhchange_to_bd


def get_content(url):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.maximize_window()
    try:
        driver.get(url=url)
        time.sleep(5)
        while True:
            with open('utils/save.html', 'w', encoding='utf-8') as file:
                file.write(driver.page_source)
            break
    except Exception as EX:
        print(EX)
    finally:
        driver.close()
        driver.quit()


def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False


def get_exchange_mod(spec):
    result = []
    with open('utils/save.html', 'r', encoding='utf-8') as file:
        f = file.read()
        soup = BeautifulSoup(f, 'html5lib')
    match spec:
        case "profinance":

            job_elements = soup.find('table', class_='stat news')
            collections = job_elements.find_all('tr')
            for element in collections:
                tds = element.find_all('td')
                for td in tds:
                    part = td.text
                    if isfloat(td.text):
                        result.append(part)
        case 'bankiros':
            job_elements = soup.find('table',
                                     class_="xxx-bd-t-light-gray xxx-table-default xxx-table-default--exchange xxx-table-default--mob-exchange")
            collections = job_elements.find_all('tr')
            collections = collections[1:]
            result = []
            for element in collections:
                td_elemennts = element.find_all('td')
                part = td_elemennts[3].text
                result.append(part)
    return result


def delete_save_html():
    file_path = "utils/save.html"
    os.remove(file_path)


def save_result(result):
    print("trying to save result")
    usd = result[1]
    eur = result[3]
    today = str(datetime.now())
    string = f"{usd}|{eur}|{today}"
    print('[INFO] starting save result', string)
    save_exhchange_to_bd(usd, eur, today)


def get__content(variant='profinance'):
    if variant == 'profinance':
        url = 'https://www.profinance.ru/chart/usdrub/'
    elif variant == 'bankiros':
        url = 'https://bankiros.ru/currency/moex/usdrub-tod'
    get_content(url)


def main(spec):
    print(f"start stealing exchange spec = {spec}")
    try:
        get__content(variant=spec)
    except Exception as ER:
        print(ER)
        value = f"UPDATE services SET status = False, report = 'Cannot to steal content from site' WHERE service_name = '{spec}';"
        insert_to_base(value)
        return
    try:
        result = get_exchange_mod(spec)
        print(result)
        save_result(result)
    except Exception as ER:
        print("[ERROR]", ER)
        value = f"UPDATE services SET status = False, report = 'Cannot to parce content' WHERE service_name = '{spec}';"
        insert_to_base(value)
        return
    delete_save_html()
    print('[INFO] STEALING EXCHANGE end loop ,all is good')
    value = f"UPDATE services SET status = True, report = 'All is good' WHERE service_name = '{spec}';"
    insert_to_base(value)


if __name__ == '__main__':
    while True:
        main(spec='profinance')
        time.sleep(3600 / 2)
        main(spec='bankiros')
        time.sleep(3600 / 2)
