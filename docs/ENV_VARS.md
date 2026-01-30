# Environment Variables

## Backend (`back/.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FLASK_ENV` | Yes | `dev` | Environment: `dev` or `prod`/`production` |
| `FLASK_PORT` | No | `5000` | Server port |
| `DOMAIN` | No | — | Production domain (e.g., `api.whatsorganizer.com.br`) |
| `HOST` | No | `0.0.0.0` | Server bind address |
| `WHISPER` | No | — | OpenAI Whisper API key (audio transcription) |
| `WHISPER_GROQ` | No | — | Groq Whisper API key (audio transcription) |
| `WHISPER_LANG` | No | `pt` | Whisper transcription language |
| `FLASK_PORT_START` | No | `3000` | Gunicorn port range start |
| `FLASK_PORT_END` | No | `3007` | Gunicorn port range end |
| `PUBLIC_API_URL` | Yes | — | Backend URL (e.g., `http://localhost:3000`) |
| `PUBLIC_FRONT_URL` | Yes | — | Frontend URL (e.g., `http://localhost:5173`) |
| `PUBLIC_MAX_UPLOAD_MB` | Yes | `40` | Maximum upload file size in MB |
| `RMQ_PORT` | No | `5672` | RabbitMQ port |
| `RMQ_HOST` | No | `rabbitmq` | RabbitMQ hostname |
| `RMQ_GID` | No | `1000` | RabbitMQ group ID |
| `RMQ_UID` | No | `1000` | RabbitMQ user ID |
| `RMQ_LINUX_USER` | No | `rabbitmq` | RabbitMQ Linux user |
| `RMQ_LINUX_GROUP` | No | `rabbitmq` | RabbitMQ Linux group |
| `HEADLESS` | No | `True` | Legacy: headless browser mode (no longer used with WeasyPrint) |
| `API_KEYS` | No | — | Comma-separated API keys for external consumers. Leave empty for open access |

## Frontend (`front/.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `HOST` | No | — | Frontend hostname |
| `PUBLIC_API_URL` | Yes | — | Backend API URL |
| `PUBLIC_FRONT_URL` | Yes | — | Frontend URL (used in sitemap, SEO) |
| `PUBLIC_NODE_ENV` | No | `development` | Node environment (`development` or `production`) |
| `PUBLIC_MAX_UPLOAD_MB` | Yes | `40` | Maximum upload size shown to users |

## Notes

- All `PUBLIC_*` variables in the frontend are accessible in client-side code via SvelteKit's `$env/static/public` and `$env/dynamic/public`
- `API_KEYS` supports multiple keys separated by commas: `API_KEYS=key1,key2,key3`
- When `API_KEYS` is empty or unset, API authentication is disabled (backwards compatible)
- RabbitMQ variables are only used in production (`FLASK_ENV=prod`)
