import json


async def health(db_pool):
    if conn := await db_pool.acquire():
        return {'status': 'available'}
    return {'status': 'unavailable'}


async def get_booking(db_pool, booking_id):
    async with db_pool.acquire() as conn:
        if booking := await conn.fetchrow(
                'SELECT * FROM bookings WHERE id = $1', booking_id):
            return _parse_booking_record(booking)
        else:
            return


async def get_booking_by_email_and_phone(db_pool, email, phone):
    async with db_pool.acquire() as conn:
        booking = await conn.fetch(
            'SELECT * FROM bookings WHERE email = $1 and phone = $2', email, phone)
        return _parse_bookings(booking)


async def get_bookings_by_limit(db_pool, page, limit):
    page, limit = int(page), int(limit)
    offset = (page - 1) * limit
    async with db_pool.acquire() as conn:
        bookings = await conn.fetch(
            'SELECT * FROM bookings limit $1 offset $2', limit, offset)
        return _parse_bookings(bookings)


async def insert_bookings(db_pool, *args):
    async with db_pool.acquire() as conn:
        status = await conn.execute('''INSERT INTO bookings VALUES ($1, $2, $3, $4, $5, $6, $7)''',
                                    *args)
        return status


def _parse_booking_record(booking):
    booking = dict(booking)
    booking['id'] = str(booking['id'])
    booking['expires_at'] = booking['expires_at'].isoformat()
    booking['offer'] = json.loads(booking['offer'])
    booking['passengers'] = json.loads(booking['passengers'])
    return booking


def _parse_bookings(bookings):
    bookings = [_parse_booking_record(record) for record in bookings]
    return bookings
