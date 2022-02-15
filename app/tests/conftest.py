import pytest

from aiohttp import web
from app import main


@pytest.fixture
def cli(event_loop, aiohttp_client):
    app = web.Application()
    app.router.add_get("/", main.serve)

    app["beanfile"] = "test"
    return event_loop.run_until_complete(aiohttp_client(app))
