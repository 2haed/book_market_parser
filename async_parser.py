import asyncio
import copy
import logging
import random
import time
import warnings
import aiohttp
import asyncpg
from data.constants import HEADERS, MOBILE_USER_AGENTS
from db.config import settings
from async_retrying import retry

warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.basicConfig(filename='data/errors.log', format='%(asctime)s| %(message)s', datefmt='%m-%d-%Y %I:%M:%S',
                    level=logging.INFO)


@retry(attempts=10)
async def get_page_data(session: aiohttp.ClientSession, connection_pool: asyncpg.Pool, offset: int, headers: dict):
    url = f'https://api.detmir.ru/v2/products?filter=categories:0;platform:web;promo:false;site:detmir;withregion:RU' \
          f'-MOW&expand=meta.facet.ages.adults,meta.facet.gender.adults,webp&meta=*&limit=502&offset={offset} '
    async with session.get(url, headers=headers) as response:
        try:
            json_file = (await response.json())
            for items in json_file['items']:
                item = {
                    'price': items['price']['price'],
                    'product_id': items['productId'],
                    'type': items['type'],
                    'article': items['article'],
                    'title': items['title'],
                    'rating': items['rating'],
                    'link': items['link']['web_url']
                }
                async with connection_pool.acquire() as connection:
                    await connection.fetch(
                        'insert into products (product_id, title, price, type, article, rating, link) values ($1, '
                        '$2, $3, $4, $5, $6, $7) ON CONFLICT (product_id) DO UPDATE set product_id = excluded.product_id',
                        int(item['product_id']), item['title'], int(item['price']), item['type'], (item['article']),
                        float(item['rating']),
                        item['link']
                    )
        except Exception as ex:
            logging.warning(ex)
            print(ex)


@retry(attempts=10)
async def main():
    connection_pool = await asyncpg.create_pool(
        user=settings.database.user, password=settings.database.password, database=settings.database.database,
        host=settings.database.host
    )

    async with connection_pool.acquire() as connection:
        await connection.fetch(
            'create table if not exists public.products (product_id int primary key, title text, price int, type text, '
            'article text, rating decimal(8, 2), link text)'
        )
    connector = aiohttp.TCPConnector(limit=50, force_close=True)
    timeout = aiohttp.ClientTimeout(total=600)
    semaphore = asyncio.Semaphore(200)
    async with semaphore:
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            url = 'https://api.detmir.ru/v2/products?filter=categories:0;platform:web;promo:false;site:detmir;withregion' \
                  ':RU-MOW&expand=meta.facet.ages.adults,meta.facet.gender.adults,webp&meta=*&limit=502 '
            async with session.get(url, headers=HEADERS) as response:
                assert response.status == 200
                length = (await response.json())['meta']['length']
                tasks = []
                for index, offset in enumerate(range(0, length, 100)):
                    await asyncio.sleep(0)
                    new_headers = copy.deepcopy(HEADERS)
                    new_headers['user-agent'] = MOBILE_USER_AGENTS[index % 10]
                    tasks.append(asyncio.create_task(get_page_data(session, connection_pool, offset, new_headers)))
                await asyncio.gather(*tasks)


if __name__ == '__main__':
    start = time.time()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    print(time.time() - start)
