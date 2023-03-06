import logging
import os
from datetime import datetime

import requests
from bs4 import BeautifulSoup

URL = "https://lovikod.ru/knigi/promokody-litres/"
LOCAL_COPY_ENV_NAME = "litres.scrape.use-local"
LOCAL_FILE_NAME_PATH = "./local"
LOCAL_FILE_NAME = "local.html"

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def date_str_until_to_obj(date_in) -> datetime:
    date_as_str = date_in.split(' ')[1]
    date_obj = datetime.strptime(date_as_str, '%d.%m.%Y')
    return date_obj


def convert_month_rus_to_eng(month_rus: str) -> str:
    """ Convert russian mont name to eng. Lowercase.
    In case of error returns "january" """
    month_rus = month_rus.lower()  # just in case
    months = {'январь': 'january',
              'февраль': 'february',
              'март': 'march',
              'апрель': 'april',
              'май': 'may',
              'июнь': 'june',
              'июль': 'july',
              'август': 'august',
              'сентябрь': 'september',
              'октябрь': 'october',
              'декабрь': 'december'}
    return months.get(month_rus, 'january')


def date_str_to_next_month_datetime_obj(date_in: str) -> datetime:
    """ Returns datetime object with next month (and next year if current month is december"""
    date_split = date_in.split(' ')
    month_str = convert_month_rus_to_eng(date_split[0])
    year_str = date_split[1]
    date_str = f'{month_str} {year_str}'
    date_obj = datetime.strptime(date_str, '%B %Y')
    next_month = date_obj.month + 1 if date_obj.month < 12 else 1
    year = date_obj.year if date_obj.month < 12 else date_obj.year + 1
    date_of_next_month = datetime(year, next_month, 1)
    return date_of_next_month


def date_str_to_date_obj(date_in: str) -> datetime:
    date_in = date_in.lower()
    if date_in.startswith('до'):
        return date_str_until_to_obj(date_in)
    return date_str_to_next_month_datetime_obj(date_in)


def strip_ampersand(code_url: str):
    amp_index = code_url.find('&')
    if amp_index != -1:
        code_url = code_url[:code_url.find("&")]
    return code_url


class Codes:
    def __init__(self):
        self.codes = []
        content = self.__get_html_content()
        soup = BeautifulSoup(content, "lxml")
        table_body = soup.find(name="tbody")
        self.__fill_codes_list(table_body)
        log.info('Codes object created')

    def __use_local_page(self) -> str:
        self.local_dir = "./local"
        self.local_path = os.path.join(LOCAL_FILE_NAME_PATH, LOCAL_FILE_NAME)
        log.debug("Local path is: %s", self.local_path)
        content = self.__get_local_page_content()
        return content

    def __get_local_page_content(self):
        if not os.path.exists(self.local_path):
            if not os.path.exists(self.local_dir):
                os.makedirs(self.local_dir)
            response = requests.get(URL)
            response.raise_for_status()
            with open(self.local_path, "wb+") as f:
                f.write(response.content)
                content = response.content
        else:
            with open(self.local_path) as f:
                content = f.read()
        return content

    def __get_html_content(self):
        use_local = bool(os.getenv(LOCAL_COPY_ENV_NAME))
        if use_local:
            content = self.__use_local_page()
        else:
            response = requests.get(URL)
            response.raise_for_status()
            content = response.content
        return content

    def __fill_codes_list(self, body):
        for row in body.find_all("tr"):
            log.info('New row iteration')
            exp_date_as_text = row.find_all_next("td")[0].text
            log.debug("Code exp. text: %s", exp_date_as_text)
            exp_date = date_str_to_date_obj(exp_date_as_text)
            exp_date_as_iso_str = exp_date.date().isoformat()
            log.debug('Code exp. date: %s', exp_date_as_iso_str)

            code = row.find_all_next("td")[1]
            if code.text.startswith("[автокод]"):
                code = code.find('a').get('href')
                log.debug('Code URL before clearance: %s', code)
                code = strip_ampersand(code)
                log.debug('Code URL after  clearance: %s', code)
            else:
                code = code.text.replace(u'\xa0', u' ').split(" ")[0]
                log.debug("Text code: %s", code)
            desc = row.find_all_next("td")[2].text
            log.debug("Code description: %s", desc)

            code_item = (code, desc, exp_date_as_iso_str)
            log.info(code_item)
            self.codes.append(code_item)

    def get_raw_codes(self):
        log.debug('Private __get_codes. <codes> size is %s', len(self.codes))
        try:
            assert len(self.codes) > 0, f"Codes list is empty"
        except AssertionError:
            log.warning('Codes list is empty')

        log.info('get_raw_codes will return %s items', len(self.codes))
        return self.codes

    @staticmethod
    def get_fresh_raw_codes():
        codes = Codes()
        return codes.get_raw_codes()
