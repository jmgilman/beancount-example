#!/bin/bash

set -e

# Activate venv
. /opt/pysetup/.venv/bin/activate

# Start gunicorn
exec gunicorn  \
    app.main:app \
    --config gunicorn_config.py \
    --worker-class aiohttp.worker.GunicornWebWorker \
    --logger-class loguricorn.Logger