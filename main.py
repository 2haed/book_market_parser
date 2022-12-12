import logging
import sys
import aiohttp
import asyncio
import warnings
import requests
from bs4 import BeautifulSoup
from constants import HOSTURL, HEADERS, URL
from fp.fp import FreeProxy

warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.basicConfig(filename='errors.log', format='%(asctime)s| %(message)s', datefmt='%m-%d-%Y %I:%M:%S',
                    level=logging.WARNING)


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
        f = lambda obj: str(obj).encode(enc, errors='backslashreplace').decode(enc)
        print(*map(f, objects), sep=sep, end=end, file=file)


async def get_page_data(session, page):
    link = f'{HOSTURL}/{page}'
    async with session.get(link, headers=HEADERS) as response:
        # items = []
        soup = BeautifulSoup(await response.text(), 'html.parser')
        references = soup.find_all('a')
        links = [link.get('href') for link in references if
                 link.get('href').startswith('https://www.detmir.ru/product/index/id/')]

        for product in links:
            session.get(product, headers=HEADERS)!!!!!!!!!!!


async def gather_data():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for page_num in range(2, 60):
            tasks.append(asyncio.create_task(get_page_data(session, page_num)))
        return await asyncio.gather(*tasks)


async def main():
    pass


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(gather_data())
