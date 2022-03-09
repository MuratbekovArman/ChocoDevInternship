import json
from unittest.mock import AsyncMock
from utils import load_data
import pytest
from aioredis import Redis


@pytest.mark.parametrize('scenario, http_status', [
    ('valid_id', 200),
    ('non-existent_id', 404),
    ('invalid_id', 422),
])
async def test_search_detail(mocker, app, scenario, http_status):
    search_id = load_data(f'tests/data/search_detail/{scenario}.txt')
    expected_json_result = json.loads(load_data(f'tests/data/search_detail/{scenario}_response.json'))
    redis_response = load_data(f'tests/data/search_detail/{scenario}_redis_response.json')
    if redis_response is not None:
        redis_response = json.loads(redis_response)
        redis_response['items'] = json.dumps(redis_response['items'])
        redis_response = json.dumps(redis_response)
        async_mock = AsyncMock(return_value=redis_response)
        mocker.patch.object(Redis, 'get', side_effect=async_mock)

    request, response = await app.asgi_client.get(f'/search/{search_id}')
    response_json = response.json

    assert response_json == expected_json_result
    assert response.status == http_status
