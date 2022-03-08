def test_search_status_sync(app):
    request, response = app.test_client.post('/search')

    assert request.method == 'POST'
    assert response.status == 500


async def test_search_status_async(app):
    request, response = await app.asgi_client.post('/search')

    assert request.method == 'POST'
    assert response.status == 500


def test_search_with_mock_ok(app, mocker, fake_search_body, search_response, fake_uuid):
    mocker.patch('uuid.uuid4', return_value=fake_uuid)

    request, response = app.test_client.post('/search', fake_search_body)

    assert request.method == 'POST'
    assert response.status == 200


def test_search_with_mock_fail(app, mocker):
    mocker.patch('uuid.uuid4', side_effect=Exception)

    request, response = app.test_client.post('/search')

    assert request.method == 'POST'
    assert response.status == 500
