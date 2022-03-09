import json
import pytest
from utils import load_data


@pytest.mark.parametrize('scenario, http_status', [
    ('ow_1adt', 200),
    ('rt_2adt_1_chd', 200),
    ('wrong_search_payload', 422),
])
async def test_search(mocker, app, scenario, http_status, fake_uuid):
    request_json = load_data(f'tests/data/search/{scenario}_request.json')
    expected_json_result = json.loads(load_data(f'tests/data/search/{scenario}_response.json'))
    provider_result = load_data(f'tests/data/search/{scenario}_provider_response.json')

    mocker.patch('code.services.http_client.search_in_provider', return_value=provider_result)
    mocker.patch('uuid.uuid4', return_value=fake_uuid)

    request, response = await app.asgi_client.post('/search', data=request_json)
    response_json = response.json

    assert response_json == expected_json_result
    assert response.status == http_status

