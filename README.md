# Whats-Organizer

Whats-Organizer é uma aplicação feita em Flask (Python) e Svelte (JavaScript) com o objetivo de arquivar conversas.

## Setup do projeto:

Crie as envs a partir dos arquivos `.env.example`, renomeie esses arquivos para `.env` e ajuste os segredos.

### Como iniciar:

Backend:
```bash
whats-organizer-monorepo ~$ cd back
whats-organizer-monorepo/back ~$ python3 -m back
```

Frontend:
```bash
whats-organizer-monorepo ~$ cd front
whats-organizer-monorepo ~$ corepack enable
whats-organizer-monorepo ~$ corepack prepare yarn@stable --activate
whats-organizer-monorepo ~$ yarn set version latest
whats-organizer-monorepo ~$ yarn install
whats-organizer-monorepo ~$ yarn dev

  VITE v5.4.8  ready in 1758 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help

# Digite o + <Enter> para abrir a aplicação no navegador automaticamente
```
