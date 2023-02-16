import os

import requests
from bs4 import BeautifulSoup

URL = "https://lovikod.ru/knigi/promokody-litres/"
LOCAL_COPY_ENV_NAME = "litres.scrape.use-local"


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
        code = row.find_all_next("td")[1]
        if code.text.startswith("[автокод]"):
            code = code.find('a').get('href')
            # code: str
            # print(code[:code.find("&")])
        else:
            code = code.text.replace(u'\xa0', u' ').split(" ")[0]
        desc = row.find_all_next("td")[2].text
        codes[code] = desc
    return codes


def main():
    content = get_html_content()
    soup = BeautifulSoup(content, "lxml")
    table_body = soup.find(name="tbody")
    codes = get_codes(table_body)

    for code in codes.items():
        print(code)


def get_html_content():
    is_local = os.getenv(LOCAL_COPY_ENV_NAME)
    if bool(is_local):
        content = use_local_page()
    else:
        response = requests.get(URL)
        response.raise_for_status()
        content = response.content
    return content


if __name__ == '__main__':
    main()
