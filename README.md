... 

ver no front


Para iniciar o Docker em modo dev com o playwright podendo ser headfull, mude a env

Use no Xserver, não garanto que funciona no wayland

Garanta que você instalou docker no modo usuário docker (sem precisar de sudo pra rodar)

```
xhost +local:docker
docker compose -f docker-compose.yml -f docker-compose.prod.yml -f docker-compose.dev.yml up --build
```
