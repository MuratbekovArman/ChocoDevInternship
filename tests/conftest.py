import os
import sys

from pytest import fixture
from sanic import Sanic

PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    os.pardir))
sys.path.insert(0, PROJECT_ROOT)


@fixture
def fake_uuid():
    return '557d187d-6465-4850-b4ea-6121752614f8'


@fixture()
def fake_search_body():
    return {
        "provider": "Amadeus",
        "cabin": "Economy",
        "origin": "ALA",
        "destination": "NQZ",
        "dep_at": "2022-03-27",
        "arr_at": "2022-03-28",
        "adults": 1,
        "children": 0,
        "infants": 0,
        "currency": "KZT"
    }


@fixture
def search_response(fake_uuid):
    return {'id': fake_uuid, 'status': 'pending', 'items': []}


@fixture()
def search_detail_response(fake_uuid):
    return {'id': fake_uuid, 'status': 'DONE', 'items': []}


@fixture
def app():
    from code import app as sanic_app

    test_app = Sanic('test-app')
    test_app.router = sanic_app.app.router
    test_app.register_listener(sanic_app.init_before, 'before_server_start')
    test_app.register_listener(sanic_app.cleanup, 'after_server_stop')

    return test_app
