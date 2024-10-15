# syntax=docker.io/docker/dockerfile:1.7-labs
# Syntax necessary for --exclude to work
FROM python:3.13.0-alpine3.20

WORKDIR /app

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY --exclude=infra . .

ARG FLASK_PORT="${FLASK_PORT}"
ARG GUNICORN_WORKERS="${GUNICORN_WORKERS}"

CMD ["sh", "-c", "gunicorn -w ${GUNICORN_WORKERS} -b 0.0.0.0:${FLASK_PORT} app:app"]