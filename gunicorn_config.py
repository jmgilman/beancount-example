import logging

from loguricorn.intercept import InterceptHandler  # type: ignore

logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO)
