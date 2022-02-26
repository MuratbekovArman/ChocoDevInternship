import aiohttp

URL = 'https://avia-api.k8s-test.aviata.team'


async def post_search(headers, body):
    results = []
    body['provider'] = 'Amadeus'
    amadeus_body = body
    body['provider'] = 'Sabre'
    sabre_body = body
    timeout = aiohttp.ClientTimeout(total=30)

    # that approach works very slowl. It must be incorrect
    async with aiohttp.ClientSession(f"{URL}", timeout=timeout) as session:
        async with session.post('/offers/search', json=amadeus_body, headers=headers) as resp:
            a_res = await resp.json()
            results.append(a_res)
        async with session.post('/offers/search', json=sabre_body, headers=headers) as resp:
            s_res = await resp.json()
            results.append(s_res)
    return results


async def booking(headers, body):
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{URL}/offers/booking", json=body, headers=headers) as resp:
            result = await resp.json()
    return result
