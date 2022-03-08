def test_search_with_mock_ok(app, mocker, search_detail_response, fake_uuid):
    mocker.patch('uuid.uuid4', return_value=fake_uuid)

    request, response = app.test_client.get(f'/search/{fake_uuid}')

    assert request.method == 'GET'
    assert response.status == 404
