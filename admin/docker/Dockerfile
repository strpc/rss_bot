FROM python:3.8-alpine as builder

COPY requirements.txt .
RUN pip install --prefix=/install -r ./requirements.txt

ARG TIMEZONE=Europe/Moscow
RUN apk upgrade --update \
  && apk add -U tzdata \
  && ln -fs /usr/share/zoneinfo/${TIMEZONE} /etc/localtime \
  && echo $TIMEZONE > /etc/timezone


# ========== final image
FROM python:3.8-alpine as production
LABEL maintainer="https://github.com/strpc"

ENV PYTHONUNBUFFERED 1

COPY --from=builder /etc/timezone /etc/timezone
COPY --from=builder /etc/localtime /etc/localtime
COPY --from=builder /install /usr/local

WORKDIR /app
COPY . /app

ENV PYTHONPATH=/app/app

VOLUME ["/app/db/"]

RUN ["chmod", "+x", "./docker/entrypoint.sh"]

ENTRYPOINT ["./docker/entrypoint.sh"]
CMD ["prod"]
