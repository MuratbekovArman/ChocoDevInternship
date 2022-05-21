import asyncio
import asyncpg
import aioredis
import json
import uuid

from sanic import Sanic, response
from sanic.exceptions import NotFound, ServerError
from sanic_scheduler import SanicScheduler, task
from datetime import datetime, date, timedelta

from .exceptions import ValidationError, NotFoundError
from .services import http_client, database, validator
from . import settings

app = Sanic('internship-web')
scheduler = SanicScheduler(app)

amadeus = 'Amadeus'
sabre = 'Sabre'


@app.get('/health')
async def health(request):
    db = request.app.ctx.db_pool
    redis = request.app.ctx.redis

    db_health = await database.health(db)
    if redis_health := await redis.client():
        redis_health = {'status': 'available'}
    else:
        redis_health = {'status': 'unavailable'}
    return response.json({
        'db_health': db_health,
        'redis_health': redis_health
    })


@app.post('/search')
async def search(request):
    redis = request.app.ctx.redis
    if body := request.json:

        if validator.search_body_validated(body):
            id = str(uuid.uuid4())
            await redis.set(id, "", ex=1200)
            await asyncio.gather(http_client.search_in_provider(amadeus, body, redis, id),
                                 http_client.search_in_provider(sabre, body, redis, id))
            return response.json({"id": id})
        else:
            raise ValidationError('Incorrect information passed!')
    raise ValidationError('Missing body of the request!')


@app.get('/search/<search_id>', error_format="json")
async def search_details(request, search_id):
    redis = request.app.ctx.redis
    if validator.is_valid_uuid(search_id):
        if search_results := await redis.get(search_id):
            search_results = json.loads(search_results)
            search_results['items'] = json.loads(search_results['items'])
            return response.json(search_results)

        raise NotFoundError('Search items not found!')
    raise ValidationError('Search_id is invalid!')


@app.get('/offers/<offer_id>')
async def offer_detail(request, offer_id):
    if validator.is_valid_uuid(offer_id):
        redis = request.app.ctx.redis
        search_keys = await redis.keys()
        for key in search_keys:
            if search_results := await redis.get(key):
                search_results = json.loads(search_results)
                if 'items' in search_results:
                    search_results['items'] = json.loads(search_results['items'])
                    for item in search_results['items']:
                        if item['id'] == offer_id:
                            return response.json(item)
        raise NotFound('Offer not found')
    raise ValidationError('Invalid offer_id!')


# after inserting field "expires_at" it changes
# from "2022-03-06T00:41:10.834617+06:00" to "2022-03-05T18:41:10.834617+00:00"
@app.post('/booking')
async def booking(request):
    body = request.json
    if validator.booking_body_validated(body):
        if result := await http_client.booking(body):
            await database.insert_bookings(request.app.ctx.db_pool,
                                           uuid.UUID(result['id']), result['pnr'],
                                           datetime.fromisoformat(result['expires_at']),
                                           result['phone'], result['email'],
                                           json.dumps(result['offer']),
                                           json.dumps(result['passengers']))
            return response.json(result)
        else:
            raise ServerError('Insert failed!')
    else:
        raise ValidationError('Incorrect information passed!')


@app.get('/booking/<booking_id>', error_format="json")
async def booking_detail(request, booking_id):
    db_pool = request.app.ctx.db_pool
    if result := await database.get_booking(db_pool, booking_id):
        return response.json(result)
    raise NotFound('Booking not found')


@app.get('/booking')
async def booking_search(request):
    db_pool = request.app.ctx.db_pool
    email, phone = request.args.get('email'), request.args.get('phone')
    page, limit = request.args.get('page'), request.args.get('limit')

    if email and phone:
        data = await database.get_booking_by_email_and_phone(db_pool,
                                                             email, phone.replace(' ', '+'))
    elif page and limit:
        data = await database.get_bookings_by_limit(db_pool, page, limit)
    else:
        raise ValidationError('Incorrect set of parameters')

    return response.json(data)


# needs to be reconfigured on updating at 12:00. Should I calculate delay manually?
@task(timedelta(hours=24))
async def get_rates(app):
    dt = date.today()

    redis = app.ctx.redis
    if rates := await redis.get(f'currency_rates:{dt.isoformat()}'):
        return response.json({
            'date': dt.isoformat(),
            'rates': json.loads(rates)
        })

    rates = await http_client.get_rates()
    await redis.set(f'currency_rates:{dt.isoformat()}', json.dumps(rates), ex=24 * 60 * 60)

    return response.json({
        'date': dt.isoformat(),
        'rates': rates
    })


app.add_task(get_rates(app))


@app.listener('before_server_start')
async def init_before(app, loop):
    app.ctx.db_pool = await asyncpg.create_pool(dsn=settings.DATABASE_URL)
    app.ctx.redis = aioredis.from_url(settings.REDIS_URL,
                                      decode_responses=True, max_connections=50)


@app.listener('after_server_stop')
async def cleanup(app, loop):
    await app.ctx.redis.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
    app.config.FALLBACK_ERROR_FORMAT = 'json'
