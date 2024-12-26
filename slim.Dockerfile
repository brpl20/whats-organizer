# syntax=docker.io/docker/dockerfile:1.7-labs
# Syntax necessary for --exclude to work

FROM python:3.12.8-slim

RUN apt-get update && apt-get upgrade -y --no-install-recommends
RUN addgroup --system python && adduser --system --ingroup python --home /home/python python
RUN apt-get install -y --no-install-recommends ffmpeg wget # libnss3 libnspr4 \
    libatk1.0-0 libatk-bridge2.0-0 \
    libatspi2.0-0 libxcomposite1 \
    libxdamage1 libcups2
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
# Video not loading, see https://github.com/microsoft/playwright/issues/4585
RUN apt -y install ./google-chrome-stable_current_amd64.deb && rm google-chrome-stable_current_amd64.deb
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

USER python
WORKDIR /app

COPY --chown=python:python requirements.txt .
RUN pip3 install --no-cache-dir --upgrade pip
ENV PATH="/home/python/.local/bin:${PATH}"
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install --no-cache-dir playwright==1.49.1
# RUN playwright install chromium

COPY --chown=python:python --exclude=infra . .

ARG FLASK_PORT_START=${FLASK_PORT_START}
ARG FLASK_PORT_END=${FLASK_PORT_END}
EXPOSE ${FLASK_PORT_START}-${FLASK_PORT_END}

CMD ["sh", "-c", "\
python -c 'from gevent import monkey; monkey.patch_all()' && \
for FLASK_PORT in $(seq ${FLASK_PORT_START} ${FLASK_PORT_END}); do \
  gunicorn -w 1 -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -b 0.0.0.0:${FLASK_PORT} app:app --timeout 300 & \
done && wait"]
