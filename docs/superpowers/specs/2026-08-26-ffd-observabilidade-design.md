# Observabilidade do WhatsOrganizer → FFD

**Data:** 26/08/2026
**Status:** desenho aprovado, aguardando plano de implementação
**Repos afetados:** `whats-organizer`, `fullFuckerDashboard`

## Problema

O WhatsOrganizer quebra em silêncio. Em 26/08/2026 descobrimos que o upload
estava quebrado desde 30/01/2026 — sete meses — por uma regressão da migração
para Svelte 5 (`Main.svelte:387`, commit `2733f499`). Ninguém percebeu porque
não existe nenhum sinal saindo do serviço: a única telemetria do backend é
`print()` para stdout do container.

Três buracos concretos, todos encontrados durante aquela investigação:

1. `conversation_processor.py:78` — `except Exception as e: return {"Erro": str(e)}`
   achata toda falha do pipeline numa string e descarta o traceback. O painel
   nunca saberia *por que* quebrou, só *que* quebrou.
2. `whatsapp_api.py:127` — o `print` global do processo é monkeypatchado por
   request. Sob gevent, com dois uploads simultâneos, o progresso de um vaza
   para o WebSocket do outro.
3. Nenhum workflow em `.github/workflows/` roda a suíte e2e. Os testes que
   pegam a regressão existem em `front/tests/e2e/index.test.js` e passam — só
   nunca rodaram depois da migração.

## O que já existe do lado do FFD

O FFD (`/home/brpl/code/fullFuckerDashboard/ai-dashboard`) já tem tudo que
precisamos. O trabalho é preencher um slot vazio, não construir um sistema.

**Ingest:** `POST /api/webhooks/usage`, autenticado por `x-webhook-token`
(ou `x-webhook-secret`, ou `?token=`). Implementado em
`app/api/webhooks/[source]/route.ts`, função `handleUsage`. Hoje aceita dois
formatos:

```jsonc
// relatório diário
{ "service": "legal_data", "date": "2026-08-25", "events": 5,
  "unique_users": 3, "top_repeats": [{ "user": "a1b2c3d4", "count": 2 }] }

// deploy / boot
{ "service": "legal_data", "event": "deploy", "version": "1.4.2" }
```

Grava em `alertEvents` com o corpo cru em `metadata` e dispara Telegram se
`shouldNotify("usage")`. Campos extras no body sobrevivem em `metadata` mesmo
sem o renderer conhecê-los.

**Uptime:** `observabilityTargets` (`lib/db/schema.ts:120`) poda uma URL num
intervalo, registra status, latência e `errorKind` (timeout / dns / connection
/ tls / http), e abre incidente após N falhas seguidas. Liga-se a um serviço
pelo campo `serviceKey`.

**`"wao"` já é chave conhecida** — aparece no placeholder do cadastro de target
(`app/observability/[id]/page.tsx:303`) e no comentário da rota. O
whats-organizer é o único que nunca emitiu nada: zero ocorrências de webhook
ou FFD no repo inteiro.

**Referência de emissor:** `prc_legal_data` faz exatamente isso —
`app/controllers/concerns/usage_tracking.rb` (grava, fire-and-forget, IP
hasheado) e `app/jobs/usage_report_job.rb` (agrega e POSTa 00:05
America/São_Paulo, manda mesmo com zero eventos).

## Restrição que define o desenho

Deploy é docker compose (`all.yml` → `back-docker.yml`; o `back.yml` com
systemd é legado e não roda). São **dois containers** de backend,
`wo-backend-0` e `wo-backend-1`, cada um `gunicorn --preload -w 1` com worker
gevent, atrás do nginx. Cada um tem hoje seu próprio volume
(`backend-N-data:/app/zip_tests`).

Um SQLite dentro de um container é por-container. Para agregar o dia inteiro
numa consulta só, o banco de eventos precisa de um volume **compartilhado**
entre os dois.

Contenção não é problema: dois processos escritores, ordem de dezenas de
writes por dia. WAL resolve com folga.

## Desenho

### 1. Coleta — `back/src/utils/events.py`

SQLite em `EVENTS_DB_PATH` (default `/app/data/events.db`), WAL ligado no
init, `busy_timeout=5000`.

```sql
CREATE TABLE IF NOT EXISTS events (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  ts          TEXT    NOT NULL,   -- ISO8601 UTC
  event_type  TEXT    NOT NULL,   -- process_zip | boot
  outcome     TEXT    NOT NULL,   -- ok | error | blocked
  ip_hash     TEXT,               -- SHA-256(ip + EVENTS_IP_SALT)
  duration_ms INTEGER,
  error_kind  TEXT,               -- classe da exceção
  error_msg   TEXT,
  traceback   TEXT,
  meta        TEXT                -- JSON: n_messages, zip_size, device, n_media
);
CREATE INDEX IF NOT EXISTS idx_events_ts ON events(ts);
```

API pública:

```python
record_process(outcome, ip_hash, duration_ms, error=None, meta=None) -> None
record_boot(version) -> None
```

Ambas fire-and-forget: qualquer exceção interna é logada e engolida. O
tracking nunca pode afetar a resposta de um upload — mesma regra do
`UsageTracking` do legal_data.

**LGPD.** Só o hash do IP com salt, nunca o IP em claro. Nada de nome de
arquivo, nada de conteúdo de conversa, nada de nome de contato. O `meta` só
carrega números e o device detectado.

Isso pesa mais aqui do que no legal_data: o produto se vende em cima de
"destruímos seus arquivos no disconnect" (`connection_handlers.py`). Um banco
de observabilidade que guardasse nome de anexo furaria a própria promessa do
produto.

### 2. Alerta imediato — `back/src/utils/ffd.py`

```python
post_ffd(payload: dict) -> None
```

POST em `FFD_WEBHOOK_URL` com header `x-webhook-token: FFD_WEBHOOK_TOKEN`.
Executado em `gevent.spawn` para não segurar a request. Timeout 5s, sem
retry — o relatório diário é a rede de segurança se o POST se perder.

Terceiro formato do contrato, novo:

```jsonc
{ "service": "wao", "event": "error",
  "error_kind": "FileProcessingError",
  "stage": "extract_zip",
  "error_msg": "Error extracting ZIP file: ...",
  "at": "2026-08-26T14:03:11Z" }
```

Sem `traceback` no payload: ele fica no SQLite local, para consulta pelo
terminal. O alerta carrega o suficiente para decidir se vale investigar.

### 3. Relatório diário — `back/scripts/daily_report.py`

Agrega o dia anterior em America/São_Paulo (mesmo fuso do legal_data) e POSTa:

```jsonc
{ "service": "wao", "date": "2026-08-25",
  "events": 5, "unique_users": 3, "top_repeats": [{ "user": "a1b2c3d4", "count": 2 }],
  "ok": 5, "errors": 0, "blocked": 0 }
```

`events` / `unique_users` / `top_repeats` continuam para não quebrar o
renderer atual do FFD. `ok` / `errors` / `blocked` são o acréscimo.

Manda mesmo com zero eventos — heartbeat.

Cron no host às 00:05, reusando a forma de `docker exec` que o
`back-docker.yml` já emprega no smoke check pós-deploy:

```
5 0 * * * docker exec wo-backend-0 python scripts/daily_report.py >> /var/log/wao-daily.log 2>&1
```

Só o `backend-0` roda: os dois enxergam o mesmo volume, um basta.

Retenção: apaga eventos com mais de 90 dias ao fim do relatório.

### 4. Onde os eventos nascem

- `app.py` rota `/process` — cronometra, hasheia o IP (respeitando
  `X-Forwarded-For`, já que roda atrás do nginx), chama `record_process`.
- `conversation_processor.py:78` — o `except Exception` guarda
  `traceback.format_exc()` no evento antes de devolver `{"Erro": str(e)}`.
  **A resposta HTTP não muda** — nada de stack vazando para o usuário.
- `app.py` no boot — `record_boot` e POST de `event: "deploy"`.

`SecurityError` vira `outcome: "blocked"`, não `"error"`: um zip malicioso
barrado é o sistema funcionando, não falhando. Contar junto poluiria o alerta.

### 5. Morte do `print` global

`ConversationProcessor.__init__` passa a receber
`progress: Callable[[str], None]`, default no-op. Cada
`print('Copying ZIP file...')` vira `self.progress('Copying ZIP file...')`.
O monkeypatch inteiro em `whatsapp_api._process_with_new_system` sai, junto
com o `progress_mapping` por interceptação de string.

Teste que prova o ganho: dois `process_conversation` concorrentes com
callbacks distintos, cada um recebe só as suas mensagens. Hoje isso falha.

### 6. Volume e configuração

`docker-compose.yml`: volume nomeado `events-data` montado em `/app/data` nos
dois backends.

Novas variáveis em `.env.backend.example`:

| Variável | Papel |
|---|---|
| `FFD_WEBHOOK_URL` | endpoint `/api/webhooks/usage` do FFD |
| `FFD_WEBHOOK_TOKEN` | valor do header `x-webhook-token` |
| `EVENTS_IP_SALT` | salt do hash de IP (LGPD) |
| `EVENTS_DB_PATH` | default `/app/data/events.db` |

Sem `FFD_WEBHOOK_URL` configurada, a emissão é pulada com log de warning e o
SQLite continua gravando — mesma degradação do `UsageReportJob`.

### 7. Lado FFD — `handleUsage`

- Branch novo para `event: "error"` → severity `critical`, título
  `wao: FileProcessingError`, mensagem com `stage` e `error_msg`.
- Relatório diário: título vira `Uso diário: wao — 5 eventos (5 ok)`; havendo
  falha, `(4 ok, 1 erro)` e severity `warning`.
- **Dia-zero deixa de ser `"sem uso (heartbeat ok)"`** e passa a severity
  `warning` com "sem uso — verificar".

Essa última é a que importa mais. Com o front quebrado, nenhum POST chegava ao
`/process`: o relatório diário teria dito `events: 0` e o FFD renderizaria
"heartbeat ok" por sete meses. Zero eventos num produto vivo é alarme, não
saúde.

Além do código: cadastrar `https://api.whatsorganizer.com.br/health` como
`observabilityTarget` com `serviceKey: "wao"`. Uptime, latência, classificação
de erro de rede e abertura de incidente — tudo já implementado, custa só o
cadastro.

### 8. CI

Somar a suíte e2e ao `all.yml`. É o buraco que deixou a regressão passar sete
meses. Sem isso, todo o resto acima é detecção pós-fato: o painel avisaria que
o uso caiu a zero, mas só depois de o deploy já estar no ar.

## Fora de escopo, deliberadamente

- **UI web neste repo.** O FFD é onde se lê. Aqui só se emite.
- **Instrumentação do `/download-pdf`.** Decisão explícita — o foco é o
  caminho de processamento.
- **Tabela por request tipo `ApiLog`.** `/process` é o único endpoint que
  carrega significado; logar `/health` e `/media/*` seria ruído.

## Testes

| Nível | O que cobre |
|---|---|
| unit | `events.py`: grava, nunca levanta, WAL ligado, IP nunca em claro |
| unit | `daily_report.py`: agregação, dia-zero, corte de retenção, fuso |
| unit | progresso isolado entre dois `process_conversation` concorrentes |
| e2e | os dois testes que já existem, agora rodando no CI |

## Ordem de implementação

1. `events.py` + testes (nada depende dele ainda)
2. Instrumentação de `/process` e do `except` do processor
3. `ffd.py` + alerta imediato
4. `daily_report.py` + cron
5. Substituição do `print` global (o mais arriscado — por último, com teste antes)
6. Volume, env, docker-compose
7. Lado FFD (repo separado)
8. e2e no CI
