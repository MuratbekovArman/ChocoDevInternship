import json
from unittest.mock import AsyncMock
from utils import load_data
import pytest


@pytest.mark.parametrize('scenario, http_status', [
    ('valid_id', 200),
    ('non-existent_id', 404),
])
async def test_booking_detail(mocker, app, scenario, http_status):
    booking_id = load_data(f'tests/data/booking_detail/{scenario}.txt')
    expected_json_result = json.loads(load_data(f'tests/data/booking_detail/{scenario}_response.json'))
    db_response = load_data(f'tests/data/booking_detail/{scenario}_db_response.json')
    if db_response is not None:
        db_response = json.loads(db_response)
        async_mock = AsyncMock(return_value=db_response)
    else:
        async_mock = AsyncMock(return_value=None)

    mocker.patch('code.services.database.get_booking', side_effect=async_mock)

    request, response = await app.asgi_client.get(f'/booking/{booking_id}')
    response_json = response.json

    assert response_json == expected_json_result
    assert response.status == http_status
