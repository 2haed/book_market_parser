import json

import aiohttp
import requests

from constants import HEADERS

dictionary = dict(items=[])
for offset in range(0, 500, 100):
    url = f"https://api.detmir.ru/v2/products?filter=brands[].id:7;categories[].alias:lego;platform:web;promo:false;site:detmir;withregion:RU-MOW&expand=meta.facet.ages.adults,meta.facet.gender.adults,webp&meta=*&limit=502&offset={offset}&sort=popularity:desc"
    response = requests.request("GET", url, headers=HEADERS)
    products = []
    for items in response.json()['items']:
        item = {
            'price': items['price']['price'],
            'productId': items['productId'],
            'type': items['type'],
            'article': items['article'],
            'title': items['title'],
            'rating': items['rating'],
            'link': items['link']['web_url'],
            'pictures': items['pictures'][0]['original']
        }
        products.append(item)
    dictionary['items'] += products

with open('json.json', 'w', encoding='UTF-8') as json_file:
    json.dump(dictionary, json_file, indent=4, ensure_ascii=False)

async def main():
    async with aiohttp.ClientSession as session:
        async with session.get()

# with open('json.json', 'r', encoding='UTF-8') as file:
#     data = json.load(file)
#     items = list()
#     for product in data['items']:
#         print(product)
