#!/usr/bin/env bash

PORT=${RSS_BOT_PORT:-11000}
LOGLEVEL=${LOGLEVEL:-INFO}

uvicorn project.asgi:application \
    --host 0.0.0.0 \
    --port $PORT \
    --log-level $LOGLEVEL
