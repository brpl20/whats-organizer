# Deployment

## GitHub Actions CI/CD

The project uses GitHub Actions for automated deployment. The workflow is located in `.github/workflows/`.

### Pipeline Overview

1. Push to `master` triggers deployment
2. Build frontend (SvelteKit) and backend artifacts
3. Deploy to production server via SSH

## Server Setup

### Prerequisites

- Ubuntu/Debian server
- Python 3.10+
- Node.js 18+ (for frontend build)
- Nginx (reverse proxy)
- RabbitMQ (WebSocket message queue for production)
- SSL certificate (Let's Encrypt / Certbot)
- WeasyPrint system dependencies

### WeasyPrint System Dependencies

```bash
sudo apt-get install -y \
  python3-cffi \
  libcairo2 \
  libpango-1.0-0 \
  libpangocairo-1.0-0 \
  libgdk-pixbuf2.0-0 \
  libffi-dev \
  shared-mime-info
```

### Backend Deployment

```bash
cd back
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Production runs via Gunicorn with gevent workers:

```bash
gunicorn -k gevent -w 8 --bind 0.0.0.0:3000 app:app
```

The port range is configured via `FLASK_PORT_START` and `FLASK_PORT_END` for multiple workers.

### Frontend Deployment

```bash
cd front
corepack enable
yarn install
yarn build
```

The SvelteKit app builds to a Node.js adapter output. Run in production:

```bash
node build
```

### Nginx Configuration

Nginx serves as reverse proxy for both frontend and backend:

- `whatsorganizer.com.br` → SvelteKit frontend (port 5173 or built node server)
- `api.whatsorganizer.com.br` → Flask backend (load balanced across ports 3000-3007)

Example upstream configuration:

```nginx
upstream flask_backend {
    server 127.0.0.1:3000;
    server 127.0.0.1:3001;
    server 127.0.0.1:3002;
    server 127.0.0.1:3003;
    server 127.0.0.1:3004;
    server 127.0.0.1:3005;
    server 127.0.0.1:3006;
    server 127.0.0.1:3007;
}

server {
    listen 443 ssl;
    server_name api.whatsorganizer.com.br;

    location / {
        proxy_pass http://flask_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### RabbitMQ

Required for production multi-process WebSocket coordination:

```bash
sudo apt-get install rabbitmq-server
sudo systemctl enable rabbitmq-server
sudo systemctl start rabbitmq-server
```

Default connection: `amqp://rabbitmq:5672`

### SSL (Let's Encrypt)

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d whatsorganizer.com.br -d www.whatsorganizer.com.br -d api.whatsorganizer.com.br
```
