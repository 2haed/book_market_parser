import json
import logging
import sys
import aiohttp
import asyncio
import warnings
import time
import requests
from bs4 import BeautifulSoup
from data.constants import HOSTURL, HEADERS
from fp.fp import FreeProxy


warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.basicConfig(filename='data/errors.log', format='%(asctime)s| %(message)s', datefmt='%m-%d-%Y %I:%M:%S',
                    level=logging.INFO)


def make_proxies(n: int) -> dict:
    dict_of_proxies = dict()
    for i in range(n):
        proxy = FreeProxy(rand=True).get()
        dict_of_proxies[''.join(proxy.split(':')[0])] = proxy
    return dict_of_proxies


def get_free_proxies(n) -> list[str]:
    proxies = []
    url = "https://free-proxy-list.net/"
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    for row in soup.find("table", class_="table table-striped table-bordered").find_all("tr")[1:n + 1]:
        tds = row.find_all("td")
        try:
            ip = tds[0].text.strip()
            port = tds[1].text.strip()
            host = f"{ip}:{port}"
            proxies.append(host)
        except IndexError:
            continue
    return proxies


def uprint(*objects, sep=' ', end='\n', file=sys.stdout):
    enc = file.encoding
    if enc == 'UTF-8':
        print(*objects, sep=sep, end=end, file=file)
    else:
        formatted = lambda obj: str(obj).encode(enc, errors='backslashreplace').decode(enc)
        print(*map(formatted, objects), sep=sep, end=end, file=file)


async def get_product_data(session, link):
    async with session.get(link, headers=HEADERS) as repsonse:
        soup = BeautifulSoup(await repsonse.text(), 'html.parser')
        items = {
            'name': soup.find('h1', class_='p_3 p_4').text if soup.find('h1', class_='p_3 p_4') is not None else None,
            'price': soup.find('div', class_='L_8').text if soup.find('div', class_='L_8') is not None else None
        }
        return items


async def get_page_data(session, page):
    link = f'{HOSTURL}/{page}'
    async with session.get(link, headers=HEADERS) as response:
        soup = BeautifulSoup(await response.text(), 'html.parser')
        body = soup.find('div', class_='dt')
        references = body.find_all('a')
        links = set(link.get('href') for link in references)
        tasks = []
        for link in links:
            tasks.append(asyncio.create_task(get_product_data(session, link)))
    return await asyncio.gather(*tasks)


async def gather_data():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for page_num in range(2, 20):
            print(f'Parsing page num: {page_num}')
            tasks.append(asyncio.create_task(get_page_data(session, page_num)))
        results = await asyncio.gather(*tasks)
        with open('data.json', 'w', encoding='utf-8') as file:
            json.dump(results, file, ensure_ascii=False, indent=4)


async def main():
    pass


if __name__ == '__main__':
    start = time.time()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(gather_data())
    print(time.time() - start)
