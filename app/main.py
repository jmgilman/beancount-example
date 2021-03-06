from __future__ import annotations

import datetime
import io
import os
import random
from dataclasses import dataclass

import aiocache  # type: ignore
from aiocache import Cache, cached  # type: ignore
from aiohttp import web
from beancount.scripts import example  # type: ignore
from loguru import logger

NAME = "beancount-example"
VERSION = "0.1.0"
NAMESPACE = "main"


@dataclass
class Settings:
    """Holds the settings for configuring the web application.

    Attributes:
        start: The start date for the random beancount data.
        end: The end date for the random beancount data.
        birth: The fictional birth date for the random beancount data.
        tmpdir: A temporary directory to store generated content
    """

    start: datetime.date | None
    end: datetime.date | None
    birth: datetime.date | None

    @staticmethod
    def from_env() -> Settings:
        """Generates a new `Settings` instance configured from the environment.

        Raises:
            InvalidSetting: If a setting contains an invalid ISO date format.

        Returns:
            A new instance of `Settings` configured from the environment.
        """
        dates = {}
        for date in ("START", "END", "BIRTH"):
            env = os.getenv(date, None)
            try:
                value = datetime.date.fromisoformat(env) if env else None
            except ValueError:
                raise InvalidSetting(
                    f"Invalid ISO date format for {date}: {env}"
                )

            dates[date.lower()] = value

        return Settings(**dates)


class InvalidSetting(Exception):
    """Raised when a setting contains an incorrect value."""

    pass


def random_beanfile(
    start: datetime.date | None = None,
    end: datetime.date | None = None,
    birth: datetime.date | None = None,
    seed: int | None = None,
):
    """Generates a randomized beancount ledger.

    Args:
        start: The optional start date for the generated entries.
        end: The optional end date for the generated entries.
        birth: The fictional birth date for the generated entries.

    Returns:
        The string contents of the randomized ledger.
    """
    if not end:
        end = datetime.date.today()

    if not start:
        start_offset = _rand_range(2, 10, seed)
        start_month = _rand_range(1, 12, seed)
        start_day = _rand_range(1, 28, seed)
        start = datetime.date(end.year - start_offset, start_month, start_day)

    if not birth:
        birth_offset = _rand_range(20, 40, seed)
        birth_month = _rand_range(1, 12, seed)
        birth_day = _rand_range(1, 28, seed)
        birth = datetime.date(end.year - birth_offset, birth_month, birth_day)

    logger.info("Generating random data using the following:")
    logger.info(f" Start: {str(start)}")
    logger.info(f" End: {str(end)}")
    logger.info(f"Birth: {str(birth)}")

    with io.StringIO() as s:
        example.write_example_file(birth, start, end, True, s)
        s.seek(0)
        return s.read()


@cached(cache=Cache.MEMORY, namespace=NAMESPACE)
async def get_beanfile(settings: Settings) -> str:
    """A cached function for generating a randomized beancount ledger.

    Args:
        settings: The settings to use when generating the ledger.

    Returns:
        The string contents of the randomized ledger.
    """
    return random_beanfile(settings.start, settings.end, settings.birth)


def get_cache():
    """Returns the active cache object.

    Returns:
        A Cache instance.
    """
    return aiocache.Cache(aiocache.Cache.MEMORY, namespace=NAMESPACE)


def get_settings(request: web.Request) -> Settings:
    """Fetches the settings from the given request context.

    Args:
        request: The Request context.

    Returns:
        The Settings instance.
    """
    return request.app["settings"]


def _rand_range(start: int, end: int, seed: int | None = None):
    """Generates a random number in a range with an optional seed value.

    Args:
        start: The starting value
        end: THe ending value
        seed: Optional seed

    Returns:
        A random integer between start and end.
    """
    if seed:
        random.seed(seed)
    return random.randrange(start, end)


async def on_startup(_):
    """Parses application settings and generates beancount data."""
    logger.info(f"{NAME} v{VERSION} starting")

    # Parse settings from environment
    logger.info("Loading settings")
    try:
        app["settings"] = Settings.from_env()
    except InvalidSetting as e:
        logger.error(str(e))
        exit(1)

    # Prime cache
    logger.info("Priming cache")
    await get_beanfile(app["settings"])

    logger.info("Ready to receive requests")


async def serve(request: web.Request):
    """Serves the stored ledger file contents."""
    logger.info(
        f'{request.remote} - "{request.method} {request.path}'
        f" {request.scheme.upper()}/"
        f'{request.version.major}.{request.version.minor}"'
    )

    if "reset" in request.query:
        logger.info("Resetting cache")
        await get_cache().clear()

    text = await get_beanfile(get_settings(request))
    return web.Response(text=text)


app = web.Application()
app.on_startup.append(on_startup)
app.router.add_get("/", serve)
