# syntax=docker.io/docker/dockerfile:1.7-labs
# Syntax necessary for --exclude to work

FROM python:3.12.8-alpine3.20

RUN apk update && apk --no-cache upgrade
RUN addgroup -S python && adduser -S python -G python
RUN apk --no-cache add ffmpeg
# Playwright (depends on glibc) https://wiki.alpinelinux.org/wiki/Running_glibc_programs
RUN apk --no-cache add gcompat libc6-compat libstdc++
ENV PY_BUILD_DEPENDS="g++ make patchelf"
RUN apk add --no-cache ${PY_BUILD_DEPENDS}
# créditos pela fix: https://github.com/jbwdevries
USER python

WORKDIR /app

COPY --chown=python:python requirements.txt .
RUN pip3 install --no-cache-dir --upgrade pip
RUN pip3 install --no-cache-dir aiohttp
ENV PATH="/home/python/.local/bin:${PATH}"
RUN pip3 install --no-cache-dir -r requirements.txt

USER root
RUN patchelf --set-interpreter /lib/ld-linux-x86-64.so.2 $(which python3)
USER python
RUN pip3 install --no-cache-dir playwright==1.49.1
USER root
RUN sh -c \
  "patchelf --set-interpreter /lib/ld-linux-x86-64.so.2 ~python/.local/lib/python*/site-packages/playwright/driver/node"
RUN apk del ${PY_BUILD_DEPENDS}
USER python

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
  gunicorn -w 1 -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -b 0.0.0.0:${FLASK_PORT} app:app --timeout 1000 & \
done && wait"]