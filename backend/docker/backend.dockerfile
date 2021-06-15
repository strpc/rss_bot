FROM python:3.8-alpine as builder

COPY requirements-backend.txt .

RUN pip install --prefix=/install -r ./requirements-backend.txt


# ========== final image
FROM python:3.8-alpine as production
LABEL maintainer="https://github.com/strpc"

ENV PYTHONUNBUFFERED 1

COPY --from=builder /install /usr/local

WORKDIR /app
COPY . /app

ENV PYTHONPATH=/app/app

VOLUME ["/app/app/db/", "/app/app/docker/logs/"]

RUN ["chmod", "+x", "./docker/backend-entrypoint.sh"]

ENTRYPOINT ["./docker/backend-entrypoint.sh"]
CMD ["prod"]
