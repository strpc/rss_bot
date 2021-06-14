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

VOLUME ["/app/db/"]
RUN ["chmod", "+x", "./docker/entrypoint-backend.sh"]

ENTRYPOINT ["sh", "./docker/entrypoint-backend.sh"]
CMD ["backend-prod"]
