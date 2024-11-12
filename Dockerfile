# syntax=docker.io/docker/dockerfile:1.7-labs
# Syntax necessary for --exclude to work

FROM python:3.13.0-alpine3.20

RUN apk update && apk --no-cache upgrade
RUN apk --no-cache add ffmpeg
RUN addgroup -S python && adduser -S python -G python

USER python

WORKDIR /app

COPY --chown=python:python requirements.txt .
RUN pip3 install --no-cache-dir --upgrade pip
ENV PATH="/home/python/.local/bin:${PATH}"
RUN pip3 install --no-cache-dir -r requirements.txt

COPY --chown=python:python --exclude=infra . .

ARG FLASK_PORT_START=${FLASK_PORT_START}
ARG FLASK_PORT_END=${FLASK_PORT_END}
EXPOSE ${FLASK_PORT_START}-${FLASK_PORT_END}

# https://flask-socketio.readthedocs.io/en/latest/deployment.html
# Por que Gevent? Eventlet é mais performático, porém escolhi gevent
# pela propagação automática de exceções (praticidade)
# Se for melhor usar eventlet, remova gevent do requirements.txt
# OBS.: É necessário usar um worker com websocket, para usar multiplos processos,
# Invocamos vários processos e usamos load balancing no nginx, caso mude
# as envs de FLASK_PORT, precisa configurar o nginx de acordo também
# -w apenas é suportado com 1 thread.
# É possível que -w possa ser usado agora, pois foi implementado redis pra lidar
# com concorrência, mas a documentação do gevent não recomenda.
# É aplicado o monkey patch para funcionar com o kumbu (Rabbitmq e multi thread)
# o monkey patch faz com que o IO seja non-blocking e mais eficiente
CMD ["sh", "-c", "\
python -c 'from gevent import monkey; monkey.patch_all()' && \
for FLASK_PORT in $(seq ${FLASK_PORT_START} ${FLASK_PORT_END}); do \
  gunicorn -w 1 -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -b 0.0.0.0:${FLASK_PORT} app:app --timeout 300 & \
done && wait"]