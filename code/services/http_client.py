import asyncio
import json
from datetime import date

import aiohttp
import xmltodict
from sanic.exceptions import SanicException
from code import settings

URL = 'https://avia-api.k8s-test.aviata.team'
RATES_URL = settings.NATIONAL_BANK_URL.format(date.today().strftime('%d.%m.%Y'))
headers = {'content-type': 'application/json',
           'accept': 'application/json'}
timeout = aiohttp.ClientTimeout(total=30)
amadeus = 'Amadeus'
sabre = 'Sabre'


async def search(body):
    search_results = await asyncio.gather(search_in_provider(amadeus, body),
                                          search_in_provider(sabre, body))
    return search_results


async def search_in_provider(provider, search_body, redis, id):
    body = {'provider': provider, **search_body}
    async with aiohttp.ClientSession(f'{URL}', timeout=timeout) as session:
        async with session.post('/offers/search', json=body, headers=headers) as response:
            search_in_provider_results = await response.json()

            search_currency = body.get('currency')
            rates = await redis.get(f'currency_rates:{date.today().isoformat()}')

            search_in_provider_results['items'] = __change_currencies(
                search_in_provider_results.get('items'),
                rates, search_currency)

            redis_search_result = await redis.get(id)
            if redis_search_result:
                items = json.loads(json.loads(redis_search_result).get('items'))
                items = [*items, *search_in_provider_results.get('items')]
                search_result = {'search_id': id, 'status': 'DONE',
                                 'items': json.dumps(items)}
            else:
                search_result = {'search_id': id, 'status': 'PENDING',
                                 'items': json.dumps(search_in_provider_results.get('items'))}

            await redis.set(id, json.dumps(search_result), ex=1200)
    return search_in_provider_results


async def booking(body):
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(f'{URL}/offers/booking', json=body, headers=headers) as resp:
            return await resp.json()


async def get_rates():
    async with aiohttp.ClientSession() as session:
        async with session.get(RATES_URL) as response:
            if response.status != 200:
                raise SanicException('Cannot fetch rates from provider')
            rates = await response.text()
            parsed = xmltodict.parse(rates)
            rates = {rate['title']: rate['description'] for rate in parsed['rates']['item']}
            return rates


def __change_currencies(items, rates, search_currency):
    rates = json.loads(rates)
    for item in items:
        item_cur = item['price']['currency']
        item_amount = item['price']['amount']
        if item_cur != search_currency:
            if item_cur == 'KZT':
                item['price']['amount'] = round(item_amount
                                                / round(float(rates.get(search_currency))))
            elif search_currency == 'KZT':
                item['price']['amount'] = item_amount * round(float(rates.get(item_cur)))
            else:
                item['price']['amount'] = round((item_amount * round(float(rates.get(item_cur))))
                                                / round(float(rates.get(search_currency))))
            item['price']['currency'] = search_currency
    return items
