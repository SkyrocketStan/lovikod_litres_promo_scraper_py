import datetime
import logging
import os

import requests
from bs4 import BeautifulSoup

from db_sqlite import DBSqlite

URL = "https://lovikod.ru/knigi/promokody-litres/"
LOCAL_COPY_ENV_NAME = "litres.scrape.use-local"
LOCAL_FILE_NAME_PATH = "./local"
LOCAL_FILE_NAME = "local.html"

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

current_date_in_iso = datetime.datetime.now().date().isoformat()
log.debug(current_date_in_iso)

def use_local_page() -> str:
    local_dir = "./local"
    local_path = os.path.join(LOCAL_FILE_NAME_PATH, LOCAL_FILE_NAME)
    log.debug("Local path is: " + local_path)
    content = get_local_page_content(local_dir, local_path)
    return content


def get_local_page_content(local_dir, local_path):
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
        exp_date_as_text = row.find_all_next("td")[0].text
        # log.debug("exp.date: " + exp_date_as_text)

        code = row.find_all_next("td")[1]
        if code.text.startswith("[автокод]"):
            code = code.find('a').get('href')
            # code: str
            # print(code[:code.find("&")])
        else:
            code = code.text.replace(u'\xa0', u' ').split(" ")[0]
        desc = row.find_all_next("td")[2].text
        # log.debug("description: " + desc)
        # log.debug("code: " + code)
        codes[code] = desc
    return codes


def main():
    log.info("main() start")
    content = get_html_content()
    soup = BeautifulSoup(content, "lxml")
    table_body = soup.find(name="tbody")
    codes = get_codes(table_body)

    sql = DBSqlite("codes")
    log.info("SQL Connected")
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
