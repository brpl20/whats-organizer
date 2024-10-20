# syntax=docker.io/docker/dockerfile:1.7-labs
# Syntax necessary for --exclude to work

FROM python:3.13.0-alpine3.20

RUN apk update && apk upgrade
RUN addgroup -S python && adduser -S python -G python

USER python

WORKDIR /app

COPY --chown=python:python requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY --chown=python:python --exclude=infra . .

ARG FLASK_PORT="${FLASK_PORT}"
ARG GUNICORN_WORKERS="${GUNICORN_WORKERS}"

ENV PATH="/home/python/.local/bin:${PATH}"
CMD ["sh", "-c", "gunicorn -w ${GUNICORN_WORKERS} -b 0.0.0.0:${FLASK_PORT} app:app"]
