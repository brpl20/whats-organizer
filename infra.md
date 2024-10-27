## Documentação da Infra:

### Logs:
Dentro do server, tudo é rodado pelo docker, para ver os logs de debug/ erro, rode:

```bash
docker ps -a
docker logs 4729c7376604 # Esse ID é apenas um exemplo
```

Para rodar comando em um container que está iniciado:

```bash
docker exec -it 9c5bf442c17c /bin/sh
```

Para rodar comando em um container morto (inicia ele):
> Neste modo é possível que alguns arquivos criados no processo de inicialização não estejam disponíveis

```bash
docker run -it whats-organizer-nginx /bin/sh
```

Renovar certificado:

O certificado do front é manejado pela cloudflare (na porta 80), mas o plano free não permite manejar outras portas, como há dois containers nginx, para manter as redes isoladas, usaremos um certificado gerado pelo certbot no backend.

Para evitar vazamento de IP (fingerprint do certificado através do Censys), foi feito um bloqueio no nginx, há um script de inicialização das regras de bloqueio baixando os IPs daqui: https://www.cloudflare.com/ips-v4/# https://www.cloudflare.com/ips-v6/# e negando quaisquer outros IPs de acessar o servidor.

Passos para gerar certificado:

```bash
. /opt/certbot/bin/activate
systemctl stop docker containerd docker.socket
certbot certonly --standalone -d api.whatsorganizer.com.br
systemctl start docker containerd docker.socket
```

Há um cronjob para executar a renovação, esse roda automagicamente de 12 em 12 horas:

```
0 0,12 * * * root bash -c '. /opt/certbot/bin/activate; python -c "import random; import time; time.sleep(random.random() * 3600)"; pip3 install --upgrade pip certbot; sudo certbot renew -q >> /var/log/certbot-renew.log 2>&1'
```

Para ver os logs de renovação:

```
less /var/log/certbot-renew.log
```

### Redis

Para o socket io não perder a sessão, é necessário usar rabbitmq (ou redis, kafka, etc). Isso porque com múltiplos processos, o socket io pode se perder caso o balancer troque de processo.
