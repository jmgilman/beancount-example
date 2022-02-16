import datetime
import os
import time
from unittest import mock

import aiocache  # type: ignore
import pytest

from app import main


def test_from_env():
    os.environ["START"] = "2022-01-01"
    os.environ["END"] = "2022-02-01"
    os.environ["BIRTH"] = "1990-01-01"

    settings = main.Settings.from_env()
    assert settings.start == datetime.date.fromisoformat(os.environ["START"])
    assert settings.end == datetime.date.fromisoformat(os.environ["END"])
    assert settings.birth == datetime.date.fromisoformat(os.environ["BIRTH"])

    os.environ["START"] = "a bad date"
    with pytest.raises(main.InvalidSetting):
        settings = main.Settings.from_env()


@mock.patch("beancount.scripts.example.write_example_file")
def test_random_beanfile(write):
    seed = time.time()

    # With defaults
    end = datetime.date.today()

    start_offset = main._rand_range(2, 10, seed)
    start_month = main._rand_range(1, 12, seed)
    start_day = main._rand_range(1, 28, seed)
    start = datetime.date(end.year - start_offset, start_month, start_day)

    birth_offset = main._rand_range(20, 40, seed)
    birth_month = main._rand_range(1, 12, seed)
    birth_day = main._rand_range(1, 28, seed)
    birth = datetime.date(end.year - birth_offset, birth_month, birth_day)

    def side_effect(date_birth, date_begin, date_end, reformat, file):
        file.write("test")

    write.side_effect = side_effect
    result = main.random_beanfile(seed=seed)
    _, _, _, _, exp_file = write.call_args.args

    assert result == "test"
    write.assert_called_once_with(birth, start, end, True, exp_file)


@mock.patch("app.main.random_beanfile")
async def test_get_beanfile(random_beanfile):
    settings = main.Settings(
        datetime.date.today(), datetime.date.today(), datetime.date.today()
    )
    random_beanfile.return_value = "test"
    result = await main.get_beanfile(settings)

    assert result == "test"
    random_beanfile.assert_called_once_with(
        datetime.date.today(), datetime.date.today(), datetime.date.today()
    )

    random_beanfile.return_value = "testing"
    result = await main.get_beanfile(settings)
    assert result == "test"


@mock.patch("aiohttp.web.Request", autospec=True)
def test_get_settings(request):
    request.app = {}
    request.app["settings"] = "test"
    result = main.get_settings(request)
    assert result == "test"


@mock.patch("app.main.get_settings")
@mock.patch("app.main.get_cache")
@mock.patch("app.main.get_beanfile")
async def test_serve(get_beanfile, get_cache, get_settings, cli):
    settings = main.Settings(None, None, None)
    cache = mock.Mock(aiocache.factory.BaseCache, autospec=True)

    get_beanfile.return_value = "test"
    get_cache.return_value = cache
    get_settings.return_value = settings

    resp = await cli.get("/")
    assert resp.status == 200
    assert await resp.text() == "test"
    get_beanfile.assert_called_with(settings)

    resp = await cli.get("/?reset")
    assert resp.status == 200
    cache.clear.assert_called_once()
