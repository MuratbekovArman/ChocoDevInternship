import asyncio
import asyncpg
import aioredis
import json
import uuid

from datetime import datetime
# from cerberus.errors import ValidationError
from sanic import Sanic, response
from .services import http_client, database, validator
from . import settings


app = Sanic('internship-web')

amadeus = 'Amadeus'
sabre = 'Sabre'


@app.post('/search')
async def search(request):
    redis = request.app.ctx.redis
    body = request.json
    if validator.search_body_validated(body):
        id = str(uuid.uuid4())
        await redis.set(id, "", ex=1200)
        await asyncio.gather(http_client.search_in_provider(amadeus, body, redis, id),
                             http_client.search_in_provider(sabre, body, redis, id))
        return response.json({"id": id})
    else:
        return response.json({
            'msg': 'Incorrect information passed!'
        })


@app.get('/search/<search_id>')
async def search_details(request, search_id):
    search_results = await request.app.ctx.redis.get(search_id)
    search_results = json.loads(search_results)
    search_results['items'] = json.loads(search_results['items'])
    return response.json(search_results)


@app.get('/offers/<search_id>/<offer_id>')
async def offer_detail(request, search_id, offer_id):
    search_results = await request.app.ctx.redis.get(search_id)
    search_results = json.loads(search_results)
    search_results['items'] = json.loads(search_results['items'])
    try:
        offer = next(item for item in search_results['items'] if item['id'] == offer_id)
        return response.json(offer)
    except StopIteration:
        return response.json({'msg': 'offer not found'})


# after inserting field "expires_at" it changes
# from "2022-03-06T00:41:10.834617+06:00" to "2022-03-05T18:41:10.834617+00:00"
@app.post('/booking')
async def booking(request):
    body = request.json
    if validator.validated(body):
        result = await http_client.booking(body)
        status = await database.insert_bookings(request.app.ctx.db_pool, uuid.UUID(result['id']), result['pnr'],
                                                datetime.fromisoformat(result['expires_at']),
                                                result['phone'], result['email'],
                                                json.dumps(result['offer']),
                                                json.dumps(result['passengers']))
    return response.json(result)


@app.get('/booking/<booking_id>')
async def booking_detail(request, booking_id):
    db_pool = request.app.ctx.db_pool
    result = await database.get_booking(db_pool, booking_id)
    return response.json(result)


@app.get('/booking')
async def booking_search(request):
    db_pool = request.app.ctx.db_pool
    email, phone = request.args.get('email'), request.args.get('phone')
    page, limit = request.args.get('page'), request.args.get('limit')

    if email and phone:
        data = await database.get_booking_by_email_and_phone(db_pool, email, phone.replace(' ', '+'))
    elif page and limit:
        data = await database.get_bookings_by_limit(db_pool, page, limit)
    else:
        # raise ValidationError('Incorrect set of parameters')
        return response.json({
            'msg': 'Incorrect set of parameters'
        })

    return response.json(data)


@app.listener('before_server_start')
async def init_before(app, loop):
    app.ctx.db_pool = await asyncpg.create_pool(dsn=settings.DATABASE_URL)
    app.ctx.redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True, max_connections=50)


@app.listener('after_server_stop')
async def cleanup(app, loop):
    await app.ctx.redis.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
