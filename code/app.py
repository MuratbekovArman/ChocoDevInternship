from sanic import Sanic, response

import asyncpg
import aioredis
import json

import code.services.aio_client as aio_client
import code.services.pg_client as pg_client
import code.settings as settings
import code.services.validator as validator

app = Sanic('internship-web')


@app.post('/search')
async def search(request):
    body = request.json
    headers = {'content-type': 'application/json',
               'accept': 'application/json'}
    results = await aio_client.post_search(headers, body)

    a_id, s_id = results[0]['search_id'], results[1]['search_id']
    a_items, s_items = results[0]['items'], results[1]['items']
    await request.app.ctx.redis.set(a_id, json.dumps(a_items))
    await request.app.ctx.redis.set(s_id, json.dumps(s_items))

    return response.json(results)


@app.get('/search/<search_id>')
async def search_details(request, search_id):
    data = await request.app.ctx.redis.get(search_id)
    data = json.loads(data)
    return response.json(data)


@app.get('/offers/<search_id>/<offer_id>')
async def offer_detail(request, search_id,  offer_id):
    data = await request.app.ctx.redis.get(search_id)
    data = json.loads(data)
    for item in data:
        if item['id'] == offer_id:
            return response.json(item)
    return response.json({"msg": "Offer not found!"})


@app.post('/booking')
async def booking(request):
    body = request.json
    headers = {'content-type': 'application/json',
               'accept': 'application/json'}
    if validator.validated(body):
        result = await aio_client.booking(headers, body)

        async with request.app.ctx.db_pool.acquire() as conn:
            await conn.execute('''INSERT INTO bookings VALUES ($1, $2, $3, $4, $5, $6, $7)''',
                               result["id"], result["pnr"], result["expires_at"],
                               result["phone"], result["email"], json.dumps(result["offer"]),
                               json.dumps(result["passengers"]))
        return response.json(result)


@app.get('/booking/<booking_id>')
async def booking_detail(request, booking_id):
    result = await pg_client.get_booking(request, booking_id)
    return response.json(result)


@app.get('/booking')
async def booking_search(request):
    keys, values = list(request.args.keys()), list(request.args.values())
    if 'email' in keys:
        data = await pg_client.get_booking_by_args(request, values[0][0], values[1][0])
    elif 'page' in keys:
        data = await pg_client.get_bookings_limit(request, values[0][0], values[1][0])
    return response.json(data)


@app.listener("before_server_start")
async def init_before(app, loop):
    app.ctx.db_pool = await asyncpg.create_pool(dsn=settings.DATABASE_URL)
    app.ctx.redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True, max_connections=50)


@app.listener("after_server_stop")
async def cleanup(app, loop):
    await app.ctx.redis.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
