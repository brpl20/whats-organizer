# Base Image
FROM nginx:alpine

# Install dependencies
# RUN apk update && apk add openssl python3 python3-dev py3-pip build-base libressl-dev musl-dev libffi-dev rust cargo iptables openrc
# RUN pip3 install pip --upgrade
# RUN pip3 install certbot-nginx # certbot

# Copy files
COPY --chown=nginx:nginx ./nginx.conf /etc/nginx/nginx.conf
COPY --chown=nginx:nginx ./ssl.conf /etc/nginx/ssl.conf
#COPY ./iptables.sh /iptables.sh
RUN sh -c 'if [ -f /var/www/html/ ]; then rm -rf /var/www/html/; fi'
RUN sh -c 'if [ -f /usr/share/nginx/html/index.html ]; then echo "" > /usr/share/nginx/html/index.html; fi'
# RUN mkdir -p /etc/openrc && touch /etc/openrc/openrc.conf
# RUN rc-update add iptables

#RUN echo '#!/sbin/openrc-run' > /etc/init.d/iptables-rate-limit && \
#    echo 'command="/iptables.sh"' >> /etc/init.d/iptables-rate-limit && \
#    echo 'command_background="true"' >> /etc/init.d/iptables-rate-limit && \
#    echo 'pidfile="/run/iptables.pid"' >> /etc/init.d/iptables-rate-limit && \
#    echo 'command_args="-p /run/iptables.pid"' >> /etc/init.d/iptables-rate-limit
#RUN chmod +x /etc/init.d/iptables-rate-limit
#RUN openrc
#RUN rc-update add iptables-rate-limit

RUN rm -rf /etc/nginx/conf.d/*.conf
# COPY ./acme.conf /etc/nginx/conf.d/

# COPY ./docker-genssl-entrypoint.d/install_ssl.sh /docker-entrypoint.d/
COPY .env .
COPY .env /

#RUN echo 'net.ipv6.conf.all.forwarding=1' >> /etc/sysctl.conf
#RUN sysctl -p /etc/sysctl.conf
#RUN echo "::1 ip6-localhost ip6-loopback" >> /etc/hosts
#RUN echo "fe00::0 ip6-localnet" >> /etc/hosts
#RUN echo "ff00::0 ip6-mcastprefix" >> /etc/hosts
#RUN echo "ff02::1 ip6-allnodes" >> /etc/hosts
#RUN echo "ff02::2 ip6-allrouters" >> /etc/hosts
#RUN echo "ff02::3 ip6-allhosts" >> /etc/hosts
#
# RUN sysctl -w net.ipv6.conf.all.disable_ipv6=0
# RUN echo "net.ipv6.conf.all.disable_ipv6 = 0" >> /etc/sysctl.conf
# RUN echo "net.ipv6.conf.all.disable_ipv6 = 0" >> /etc/sysctl.conf && \
#     sysctl -p

# Set permissions
#RUN chmod +x /docker-entrypoint.d/install_ssl.sh
#RUN chmod +x /iptables.sh
#RUN chmod +x /etc/init.d/iptables-rate-limit

EXPOSE 443
EXPOSE 80

