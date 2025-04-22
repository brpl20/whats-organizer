... 

Ver no front [todo](https://github.com/brpl20/whats-organizer-front/blob/master/td.md) [infra](https://github.com/brpl20/whats-organizer-front/blob/master/explain.txt) 

## Documentação na Wiki
Ver [wiki](https://github.com/brpl20/whats-organizer/wiki)

# Pip (Dependências python)
> Para compatibilidade, rode sempre o pip dentro do docker, usando sh, você pode habilitar os scripts utilitários para criar uma função pip que roda dentro do docker.
>
> Exemplo: Fazer freeze
```bash
┌──(.venv)─(skid㉿gentoo)-[~/My_Code/whats-organizer]
└─$ . ./scripts/aliases.sh        
┌──(.venv)─(skid㉿gentoo)-[~/My_Code/whats-organizer]
└─$ pip3 freeze > requirements.txt                                     
[+] Running 3/3
 ✔ Container rabbitmq-socketio           Running0.0s 
 ✔ Container flask                       Running0.0s 
 ✔ Container nginx-whats-organizer_back  Running0.0s
```

# Windows
> Use wsl?


# Env

> renomear arquivo `.env.example` para `.env`
>
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
>
> Se der problemas, tente remover o arquivo dev.yml, ele serve só para debugging do playwright em máquinas Linux


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

Pra fazer rebuild do flask caso tenha mudado algum arquivo:
```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml -f docker-compose.prod.yml up flask --build
```

# Deploy

> commit na main, com github actions, faz deploy no push
> 
> Verifique as logs de build, mesmo que esteja com "OK"


## Como testar o playwright no linux?

> Para testar o playwright, precisa usar Xorg server e passar permissões com xhost
>
> Permitir root acessar o ambiente gráfico

```bash
xhost local:root
```

E aí habilite a env do playwright
```bash
# False para mostrar o chromium ao imprimir
HEADLESS=False
```

