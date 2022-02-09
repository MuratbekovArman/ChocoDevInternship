from sanic import Sanic, response
import aiohttp

URL = 'https://avia-api.k8s-test.aviata.team'

app = Sanic('sample-web-service')


@app.post('/search')
async def search(request):
    result = ''
    body = request.json
    headers = {'content-type': 'application/json',
               'accept': 'application/json'}
    async with aiohttp.ClientSession() as session:
        async with session.post(URL+"/offers/search", json=body, headers = headers) as resp:
            result = await resp.json()
    return response.json(result)
            

@app.get('/search/<search_id>')
async def search_details(request, search_id):
    result = ''
    headers = {'content-type': 'application/json',
               'accept': 'application/json'}
    # async with aiohttp.ClientSession() as session:
    #     async with session.get(URL + "/" + search_id,  headers = headers) as resp:
    #         result = await resp.json()
    return response.json(result)

@app.get('/offers/<offer_id>')
async def offer_detail(request, offer_id):
    result = ''
    headers = {'content-type': 'application/json',
               'accept': 'application/json'}
    async with aiohttp.ClientSession() as session:
        async with session.get(URL+ "/offers/" + offer_id, headers = headers) as resp:
            result = await resp.json()
    return response.json(result)

@app.post('/booking')
async def booking(request):
    result = ''
    body = request.json
    headers = {'content-type': 'application/json',
               'accept': 'application/json'}
    async with aiohttp.ClientSession() as session:
        async with session.post(URL+"/offers/booking", json=body, headers = headers) as resp:
            result = await resp.json()
    return response.json(result)

@app.get('/booking/<booking_id>')
async def booking_detail(request, booking_id):
    result = ''
    headers = {'content-type': 'application/json',
               'accept': 'application/json'}
    async with aiohttp.ClientSession() as session:
        async with session.get(URL+ "/booking/" + booking_id, headers = headers) as resp:
            result = await resp.json()
    return response.json(result)

@app.get('/booking')
async def booking_byArgs(request):
    results = {request.query_args}
    return response.json(results)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
