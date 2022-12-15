import asyncio
import logging
import time
import warnings
import aiohttp
import asyncpg
from data.constants import HEADERS
from db.config import con

warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.basicConfig(filename='data/errors.log', format='%(asctime)s| %(message)s', datefmt='%m-%d-%Y %I:%M:%S',
                    level=logging.INFO)


async def get_page_data(session, offset: int):
    connection = await asyncpg.connect(user=con['user'], password=con['password'], database=con['database'],
                                       host=con['host'])
    url = f'https://api.detmir.ru/v2/products?filter=brands[].id:7;categories[' \
          f'].alias:lego;platform:web;promo:false;site:detmir;withregion:RU-MOW&expand=meta.facet.ages.adults,' \
          f'meta.facet.gender.adults,webp&meta=*&limit=100&offset={offset} '
    async with session.get(url, headers=HEADERS) as response:
        assert response.status == 200
        for items in (await response.json())['items']:
            item = {
                'price': items['price']['price'],
                'product_id': items['productId'],
                'type': items['type'],
                'article': items['article'],
                'title': items['title'],
                'rating': items['rating'],
                'link': items['link']['web_url'],
                'picture': items['pictures'][0]['original']
            }
            await connection.fetch(
                'insert into products (product_id, title, price, type, article, rating, link, picture) values ($1, '
                '$2, $3, $4, $5, $6, $7, $8) ON CONFLICT (product_id) DO UPDATE set product_id = excluded.product_id',
                int(item['product_id']), item['title'], int(item['price']), item['type'], int(item['article']),
                float(item['rating']),
                item['link'], item['picture']
            )
        print(f'Parsing: {offset}')


async def main():
    connection = await asyncpg.connect(user=con['user'], password=con['password'], database=con['database'],
                                       host=con['host'])
    await connection.fetch(
        'create table if not exists public.products (product_id int primary key, title text, price int, type text, '
        'article int, rating decimal(8, 2), link text, picture text) '

    )
    async with aiohttp.ClientSession() as session:
        tasks = []
        for offset in range(0, 500, 100):
            tasks.append(asyncio.create_task(get_page_data(session, offset)))
        await asyncio.gather(*tasks)
        await connection.close()


if __name__ == '__main__':
    start = time.time()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    print(time.time() - start)
