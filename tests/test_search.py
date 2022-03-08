import json

import pytest

from code.services import validator


@pytest.mark.parametrize('args, expected_status', [
    ('', 422),
    (json.dumps({
        "cabin": "Eco",
        "origin": "ALA",
        "destination": "NQZ",
        "dep_at": "2022-03-27",
        "arr_at": "2022-03-28",
        "adults": 1,
        "children": 0,
        "infants": 0,
        "currency": "KZT"}), 422),
])
async def test_search_status_fail_async(app, args, expected_status):
    request, response = await app.asgi_client.post('/search', data=args)

    assert request.method == 'POST'
    assert response.status == expected_status


async def test_search_with_mock_ok(app, fake_search_body, search_response, fake_uuid):

    request, response = await app.asgi_client.post('/search', data=json.dumps(fake_search_body))

    assert request.method == 'POST'
    assert response.status == 200
    assert validator.is_valid_uuid(response.json.get('id'))

# def test_search_with_mock_fail(app, mocker):
#     mocker.patch('uuid.uuid4', side_effect=Exception)
#
#     request, response = app.test_client.post('/search')
#
#     assert request.method == 'POST'
#     assert response.status == 500
