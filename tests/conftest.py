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
    return 'ecfa5dfc-b44c-4576-a8f1-03ca50990879'


@fixture
def app():
    from code import app as sanic_app

    test_app = Sanic('test-app')
    test_app.router = sanic_app.app.router
    test_app.register_listener(sanic_app.init_before, 'before_server_start')
    test_app.register_listener(sanic_app.cleanup, 'after_server_stop')

    return test_app
