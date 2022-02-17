FROM python:3.10-slim-bullseye as python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.1.12 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

ENV PORT 8001

FROM python-base as builder-base

# Update and install deps
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install --no-install-recommends -y build-essential curl

# Install Poetry
RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python

# Install runtime deps
WORKDIR $PYSETUP_PATH
COPY ./poetry.lock ./pyproject.toml ./
RUN poetry install --no-dev

FROM python-base as production

# Add non-root user
RUN addgroup --system app && adduser --system --group app

# Update
RUN apt-get update \
    && apt-get upgrade -y

# Copy poetry and runtime deps
COPY --from=builder-base $VENV_PATH $VENV_PATH

# Copy entrypoint
COPY ./docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Copy config
COPY ./gunicorn_config.py /run/gunicorn_config.py

# Copy app
COPY ./app /run/app
WORKDIR /run

USER app

ENTRYPOINT [ "/docker-entrypoint.sh" ]