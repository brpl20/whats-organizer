... 

Ver no front [todo](https://github.com/brpl20/whats-organizer-front/blob/master/td.md) [infra](https://github.com/brpl20/whats-organizer-front/blob/master/explain.txt) 

## Documentação na Wiki
Ver [wiki](https://github.com/brpl20/whats-organizer/wiki)


# Env

> renomear arquivo `.env.example` para `.env`
> Na pasta infra também tem um .env

# Iniciar projeto completo

> Modifique `infra/server/default.conf.template`
>
> Não comite esse arquivo, apeanas desabilite a proteção de segurança localmente!

Remova:

```bash
    if ($host !~* ^(${NGINX_HOST})$) {
        return 444;
    }
```

> Todo: Isso deveria ser uma env (se possível??)



> server e infra simulada, sem hot reloading
```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml -f docker-compose.prod.yml up
```

> Para não precisar reiniciar todos os containers no docker, gosto de subir prod no terminal, e o resto em background com `up -d`


```bash
┌──(.venv)─(skid㉿gentoo)-[~/My_Code/whats-organizer]
└─$ docker compose -f docker-compose.yml -f docker-compose.dev.yml -f docker-compose.prod.yml up -d
[+] Running 3/3
 ✔ Container rabbitmq-socketio           Started                                                                 0.4s 
 ✔ Container flask                       Started                                                                 0.4s 
 ✔ Container nginx-whats-organizer_back  Started  
┌──(.venv)─(skid㉿gentoo)-[~/My_Code/whats-organizer]
└─$ docker compose -f docker-compose.yml -f docker-compose.dev.yml -f docker-compose.prod.yml up flask
[+] Running 1/0
 ✔ Container flask  Running                                                                                      0.0s 
Attaching to flask
```

> Assim, se eu der ctrl-c, vai apenas finalizar o python, e aí eu posso subir apenas o flask novamente

Pra fazer rebuild do flask:
```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml -f docker-compose.prod.yml up flask --build
```

# Deploy

> commit na main, com github actions, faz deploy no push
>
> Verifique as logs de build, mesmo que esteja com "OK"

