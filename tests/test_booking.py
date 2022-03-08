import json

from pytest import fixture


@fixture()
def fake_booking_body():
    b = {
        "offer_id": "123",
        "phone": "+77777777777",
        "email": "user@example.com",
        "passengers": [
            {
                "gender": "M",
                "type": "ADT",
                "first_name": "Craig",
                "last_name": "Bensen",
                "date_of_birth": "1985-08-24",
                "citizenship": "US",
                "document": {
                    "number": "N2343545634",
                    "expires_at": "2025-08-24",
                    "iin": "123456789123"
                }
            }
        ]
    }
    return json.dumps(b)


async def test_booking_status_fail_async(app, fake_booking_body):
    request, response = await app.asgi_client.post('/booking', data=fake_booking_body)

    assert request.method == 'POST'
    assert response.status == 422
