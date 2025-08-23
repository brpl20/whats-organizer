FROM rabbitmq:alpine

ARG RMQ_PORT
ARG RMQ_GID
ARG RMQ_UID
ARG RMQ_LINUX_USER
ARG RMQ_LINUX_GROUP
ENV RMQ_GID=${RMQ_GID}
ENV RMQ_UID=${RMQ_UID}
ENV RMQ_LINUX_USER=${RMQ_LINUX_USER}
ENV RMQ_LINUX_GROUP=${RMQ_LINUX_GROUP}
ENV RMQ_PORT=${RMQ_PORT}

ARG LOCALE_GEN
ARG TZ
ARG LANG
ARG LANGUAGE
ARG LC_ALL

ENV LOCALE_GEN="${LOCALE_GEN}"
ENV TZ="${TZ}"
ENV MUSL_LOCALE_DEPS="cmake make musl-dev gcc gettext-dev"
ENV MUSL_LOCPATH="/usr/share/i18n/locales/musl"
ENV LANG="${LANG}"
ENV LANGUAGE="${LANGUAGE}"
ENV LC_ALL="${LC_ALL}"

# Setup Locale
RUN apk add --no-cache $MUSL_LOCALE_DEPS libintl \
    && wget https://gitlab.com/rilian-la-te/musl-locales/-/archive/master/musl-locales-master.zip \
    && unzip musl-locales-master.zip \
    && cd musl-locales-master \
    && cmake -DLOCALE_PROFILE=OFF -D CMAKE_INSTALL_PREFIX:PATH=/usr . \
    && make \
    && make install \
    && cd .. \
    && rm -r musl-locales-master musl-locales-master.zip \
    && apk add --no-cache tzdata \
    && cp /usr/share/zoneinfo/America/Sao_Paulo /etc/localtime \
    && echo "${TZ}" > /etc/timezone \
    && echo "${LOCALE_GEN}" > /etc/locale.gen \
    # Add rabbitmq user/ group
    && if getent passwd ${RMQ_LINUX_USER} > /dev/null ; then deluser ${RMQ_LINUX_USER}; fi \
    && if getent group ${RMQ_LINUX_GROUP} > /dev/null; then delgroup ${RMQ_LINUX_GROUP}; fi \
    && addgroup -S ${RMQ_LINUX_GROUP} -g ${RMQ_GID} \
    && adduser -S -D -H -h /home/${RMQ_LINUX_USER} -s /bin/bash -G ${RMQ_LINUX_GROUP} ${RMQ_LINUX_USER} -u ${RMQ_UID} \
    && if [ ! -d /home/${RMQ_LINUX_USER} ]; then mkdir -p /home/${RMQ_LINUX_USER}; fi \
    && chown rabbitmq:rabbitmq /home/rabbitmq \
    && chmod 700 /home/rabbitmq \
    # Cleanup
    && apk del $MUSL_LOCALE_DEPS \
    && rm -rf /var/cache/apk/*


EXPOSE "${RMQ_PORT}"
