# WhatsApp Organizer

WhatsApp Organizer is an open-source tool for archiving and organizing WhatsApp conversations. Upload an exported `.zip` file and get a structured, searchable view of your chat with media support and PDF export.

Built with **Flask** (Python) and **SvelteKit** (JavaScript).

## Features

- Process WhatsApp exported ZIP files (iOS and Android)
- Structured chat view with WhatsApp-styled message bubbles
- Media support: images, videos, audio, PDFs, Word documents
- Audio transcription via Whisper API
- PDF export of conversations
- LGPD-compliant automatic file deletion
- Real-time processing progress via WebSocket
- Malware detection in uploaded files

## Quick Start

### 1. Setup environment files

```bash
cp back/.env.example back/.env
cp front/.env.example front/.env
```

Edit both `.env` files with your configuration.

### 2. Backend

```bash
cd back
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

### 3. Frontend

```bash
cd front
corepack enable
yarn install
yarn dev
```

Open `http://localhost:5173` in your browser.

## Documentation

| Document | Description |
|----------|-------------|
| [Architecture](docs/ARCHITECTURE.md) | System overview, modules, data flow |
| [API Reference](docs/API.md) | All endpoints with request/response examples |
| [Deployment](docs/DEPLOYMENT.md) | CI/CD, server setup, Nginx, RabbitMQ, SSL |
| [Development](docs/DEVELOPMENT.md) | Local setup, testing, linting |
| [Environment Variables](docs/ENV_VARS.md) | All env vars for backend and frontend |

## License

Open source. See repository for details.
