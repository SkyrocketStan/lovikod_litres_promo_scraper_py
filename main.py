import logging
import os

import requests
from bs4 import BeautifulSoup

from db_sqlite import DBSqlite

URL = "https://lovikod.ru/knigi/promokody-litres/"
LOCAL_COPY_ENV_NAME = "litres.scrape.use-local"

log_main = logging.getLogger(__name__)
log_main.setLevel(logging.DEBUG)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def use_local_page() -> str:
    local_file_name = "local.html"
    local_dir = "./local"
    local_path = os.path.join(local_dir, local_file_name)
    if not os.path.exists(local_path):
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)
        response = requests.get(URL)
        response.raise_for_status()
        with open(local_path, "wb+") as f:
            f.write(response.content)
            content = response.content
    else:
        with open(local_path) as f:
            content = f.read()

    return content


def get_codes(body) -> dict:
    codes = dict()

    for row in body.find_all("tr"):
        datemark = row.find_all_next("td")[0].text
        log_main.debug("datemark: " + datemark)
        code = row.find_all_next("td")[1]
        if code.text.startswith("[автокод]"):
            code = code.find('a').get('href')
            # code: str
            # print(code[:code.find("&")])
        else:
            code = code.text.replace(u'\xa0', u' ').split(" ")[0]
        desc = row.find_all_next("td")[2].text
        log_main.debug("desc: " + desc)
        log_main.debug("code: " + code)
        codes[code] = desc
    return codes


def main():
    log_main.info("main() start")
    content = get_html_content()
    soup = BeautifulSoup(content, "lxml")
    table_body = soup.find(name="tbody")
    codes = get_codes(table_body)

    sql = DBSqlite("codes")
    log_main.info("SQL Connected")
    # sql.connect_to_db()
    sql.disconnect()
    # for code in codes.items():
    #     print(code)


def get_html_content():
    use_local = bool(os.getenv(LOCAL_COPY_ENV_NAME))
    if use_local:
        content = use_local_page()
    else:
        response = requests.get(URL)
        response.raise_for_status()
        content = response.content
    return content


if __name__ == '__main__':
    main()
