FROM python:3.8-alpine as builder

COPY requirements-worker.txt requirements.txt
RUN pip install --prefix=/install -r ./requirements.txt

ARG TIMEZONE=Europe/Moscow
RUN apk add --no-cache tzdata \
  && ln -fs /usr/share/zoneinfo/${TIMEZONE} /etc/localtime \
  && echo $TIMEZONE > /etc/timezone


# ========== final image
FROM python:3.8-alpine as production
LABEL maintainer="https://github.com/strpc"

ENV PYTHONUNBUFFERED 1

RUN adduser --uid 1000 --home /app --disabled-password --gecos "" worker && \
    chown -hR worker: /app

WORKDIR /app

COPY --from=builder /etc/timezone /etc/timezone
COPY --from=builder /etc/localtime /etc/localtime
COPY --from=builder /install /usr/local

COPY --chown=worker:worker . /app

ENV PYTHONPATH=/app/app

VOLUME ["/app/app/db/", "/app/app/docker/logs/"]

RUN chmod +x ./docker/worker-entrypoint.sh

USER worker

ENTRYPOINT ["./docker/worker-entrypoint.sh"]
