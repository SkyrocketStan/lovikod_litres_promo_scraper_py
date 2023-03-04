import logging
import os

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


class Codes:
    def __init__(self):
        self.codes = []
        content = self.__get_html_content()
        soup = BeautifulSoup(content, "lxml")
        table_body = soup.find(name="tbody")
        self.__get_codes_list(table_body)
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

    def __get_codes_list(self, body):
        for row in body.find_all("tr"):
            exp_date_as_text = row.find_all_next("td")[0].text
            log.debug("exp.date: " + exp_date_as_text)

            code = row.find_all_next("td")[1]
            if code.text.startswith("[автокод]"):
                code = code.find('a').get('href')
                # code: str
                # print(code[:code.find("&")])
            else:
                code = code.text.replace(u'\xa0', u' ').split(" ")[0]
            desc = row.find_all_next("td")[2].text
            log.debug("description: " + desc)
            log.debug("code: " + code)
            self.codes.append((code, desc, exp_date_as_text))

    def __get_raw_codes(self):
        log.debug('Private __get_codes. <codes> size is %s', len(self.codes))
        try:
            assert len(self.codes) > 0, f"Codes list is empty"
        except AssertionError:
            log.warning('Codes list is empty')
        return self.codes

    @staticmethod
    def get_fresh_raw_codes():
        codes = Codes()
        log.info('Static codes()')
        return codes.__get_raw_codes()
