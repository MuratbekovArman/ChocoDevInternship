import json
from unittest.mock import AsyncMock
import pytest
from utils import load_data


@pytest.mark.parametrize('scenario, http_status', [
    ('valid', 200),
    ('invalid', 422)
])
async def test_booking(mocker, app, scenario, http_status):
    request_json = load_data(f'tests/data/booking/{scenario}_request.json')
    expected_json_result = json.loads(load_data(f'tests/data/booking/{scenario}_response.json'))
    if http_client_result := load_data(f'tests/data/booking/{scenario}_http_client_response.json'):
        http_client_result = json.loads(load_data(f'tests/data/booking/{scenario}_http_client_response.json'))
        mocker.patch('code.services.http_client.booking', return_value=http_client_result)
    mocker.patch('code.services.database.insert_bookings', side_effect=AsyncMock(return_value=None))

    request, response = await app.asgi_client.post('/booking', data=request_json)
    response_json = response.json

    assert response_json == expected_json_result
    assert response.status == http_status

