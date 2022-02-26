import json


# temporary solution
def parse_booking_record(data):
    data = dict(data)
    offer = json.loads(data['offer'])
    passengers = json.loads(data['passengers'])
    data['offer'] = offer
    data['passengers'] = passengers
    return data


def parse_bookings(data):
    data = [parse_booking_record(r) for r in data]
    return data


async def get_booking(request, booking_id):
    async with request.app.ctx.db_pool.acquire() as conn:
        data = await conn.fetchrow(
            'SELECT * FROM bookings WHERE id = $1', booking_id)
        data = parse_booking_record(data)
        return data


# plus sign in the args disappears
async def get_booking_by_args(request, email, phone):
    async with request.app.ctx.db_pool.acquire() as conn:
        data = await conn.fetchrow(
            'SELECT * FROM bookings WHERE email = $1 and phone = $2', email, phone.replace(" ", "+"))
        data = parse_booking_record(data)
        return data


async def get_bookings_limit(request, page, limit):
    page, limit = int(page), int(limit)
    offset = (page - 1) * limit
    async with request.app.ctx.db_pool.acquire() as conn:
        data = await conn.fetch(
            'SELECT * FROM bookings limit $1 offset $2', limit, offset)
        data = parse_bookings(data)
        return data
