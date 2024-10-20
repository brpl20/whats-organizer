# syntax=docker.io/docker/dockerfile:1.7-labs
# Syntax necessary for --exclude to work

FROM python:3.13.0-alpine3.20

RUN apk update && apk upgrade
RUN addgroup -S python && adduser -S python -G python

USER python

WORKDIR /app

COPY --chown=python:python requirements.txt .
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

COPY --chown=python:python --exclude=infra . .

ARG FLASK_PORT="${FLASK_PORT}"
ARG GUNICORN_WORKERS="${GUNICORN_WORKERS}"

ENV PATH="/home/python/.local/bin:${PATH}"
# https://stackoverflow.com/questions/62629125/unable-to-connect-to-flask-socketio-with-invalid-session-id-error
CMD ["sh", "-c", "gunicorn -w ${GUNICORN_WORKERS} -k gevent -b 0.0.0.0:${FLASK_PORT} app:app"]
