async def test_search_detail_with_mock_fail(app, fake_uuid):
    request, response = await app.asgi_client.get(f'/offers/{fake_uuid}')
    assert request.method == 'GET'
    assert response.status == 404
