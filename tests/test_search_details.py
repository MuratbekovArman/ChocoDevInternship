import json
from unittest.mock import AsyncMock

import pytest
from pytest import fixture

from aioredis import Redis


@fixture()
def fake_redis_search_response(fake_uuid):
    r = {
        "search_id": "557d187d-6465-4850-b4ea-6121752614f8",
        "status": "DONE",
        "items": "[]"
    }
    return json.dumps(r)


@pytest.mark.parametrize('args, expected_status', [
    ('557d187d-6465-4850-b4ea-6121752614f8', 404),
    ('557d187d-6465-4850-b4ea-6121752614f81', 422),
])
async def test_search_detail_with_mock_fail(app, args, expected_status):
    request, response = await app.asgi_client.get(f'/search/{args}')
    assert request.method == 'GET'
    assert response.status == expected_status


async def test_search_detail_with_mock_ok(mocker, app, fake_uuid, fake_redis_search_response):
    async_mock = AsyncMock(return_value=fake_redis_search_response)
    mocker.patch.object(Redis, 'get', side_effect=async_mock)

    request, response = await app.asgi_client.get(f'/search/{fake_uuid}')

    assert request.method == 'GET'
    assert response.status == 200
