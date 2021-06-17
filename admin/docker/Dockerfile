FROM python:3.8-alpine as builder

COPY requirements.txt .

RUN pip install --prefix=/install -r ./requirements.txt


# ========== final image
FROM python:3.8-alpine as production
LABEL maintainer="https://github.com/strpc"

ENV PYTHONUNBUFFERED 1

COPY --from=builder /install /usr/local

COPY . /app

WORKDIR /app
ENV PYTHONPATH=/app/app

VOLUME ["/app/db/"]
RUN ["chmod", "+x", "./docker/entrypoint.sh"]

ENTRYPOINT ["./docker/entrypoint.sh"]
CMD ["prod"]
