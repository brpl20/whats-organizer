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
└─$ . ./scripts/aliases.sh        # Dessa forma, todos os comandos pip estarão sendo redirecionados pro docker
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

## ⏱️ Timeouts e Limites do Sistema

### Conexão WebSocket
- **Backend (SocketIO)**: `ping_timeout=80` segundos
- **Frontend**: 
  - Timeout de conexão inicial: `5 segundos`
  - Tentativas de reconexão: `5 tentativas automáticas`
  - Transports: websocket, polling, webtransport

### Limites de Upload
- **Tamanho na memória**: `50MB` (MAX_FORM_MEMORY_SIZE)
- **Tamanho total**: Sem limite (MAX_CONTENT_LENGTH = None)
- **ZIP extraído**: Máximo `500MB`
- **Arquivos por ZIP**: Máximo `10.000` arquivos
- **Taxa de compressão**: Máximo `10:1`

### Segurança
- **Detecção de malware**: Bloqueia arquivos `.sh`, `.bat`, `.exe`, `.dll`, etc.
- **Directory traversal**: Proteção contra `../` em nomes de arquivo
- **CORS**: Configurado para domínios específicos

### Limitações Conhecidas
- Grupos do WhatsApp não são suportados
- Tamanho máximo: 100MB
- Não há garantia de autenticidade dos arquivos
- Processamento pode demorar para arquivos grandes (sem timeout específico)

# TD
- Backend: Ajustar tamanho máximo para 100mb e melhorar timeout
- Backend: Organizar melhor estrutura do /backend
- Frontend: Informar versões de dispositivos testados e aprovados: Android XYZ, Iphone XYZ;
- Frontend: Adicionar vídeo educacional
- Frontend: Ajustar mensagem de erro
- Frontend: Trazer repositório do frontend
- Documentação: Revisar documentação em geral
- DevOps: Arrumar servidor e hospedagem
- Testes: Criar mais arquivos de testes
- Testes: Remover testes sensíveis (add to .ignore)
- Testes: Automatizar e criar logger / mensageria de testes

.
