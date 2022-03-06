import asyncio
import json
import aiohttp

URL = 'https://avia-api.k8s-test.aviata.team'
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
            booking_response = await resp.json()
    return booking_response
