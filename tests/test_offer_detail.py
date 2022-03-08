import pytest


@pytest.mark.parametrize('args, expected_status', [
    ('557d187d-6465-4850-b4ea-6121752614f8', 404),
    ('123', 422),
])
async def test_offer_detail_with_mock_fail(app, args, expected_status):
    request, response = await app.asgi_client.get(f'/offers/{args}')
    assert request.method == 'GET'
    assert response.status == expected_status
