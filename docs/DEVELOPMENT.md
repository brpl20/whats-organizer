# Development

## Prerequisites

- Python 3.10+
- Node.js 18+
- Yarn (via corepack)
- WeasyPrint system dependencies (see [DEPLOYMENT.md](DEPLOYMENT.md))

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/brpl20/whats-organizer.git
cd whats-organizer
```

### 2. Environment files

Copy `.env.example` files and adjust values:

```bash
cp back/.env.example back/.env
cp front/.env.example front/.env
```

### 3. Backend

```bash
cd back
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

The backend starts at `http://localhost:3000` by default (configurable via `FLASK_PORT`).

### 4. Frontend

```bash
cd front
corepack enable
corepack prepare yarn@stable --activate
yarn install
yarn dev
```

The frontend starts at `http://localhost:5173`.

## Scripts

### Backend

| Command | Description |
|---------|-------------|
| `python app.py` | Start development server |
| `python -m back` | Alternative start method |

### Frontend

| Command | Description |
|---------|-------------|
| `yarn dev` | Start development server |
| `yarn build` | Production build |
| `yarn preview` | Preview production build |
| `yarn check` | Run svelte-check type checking |
| `yarn lint` | Run Prettier + ESLint |
| `yarn format` | Auto-format with Prettier |
| `yarn test:unit` | Run unit tests (Vitest) |
| `yarn test:e2e` | Run end-to-end tests (Playwright) |

## Project Structure

See [ARCHITECTURE.md](ARCHITECTURE.md) for full details.

## Testing

### Unit Tests

```bash
cd front
yarn test:unit
```

Uses Vitest with jsdom environment. Test setup is in `tests/setup.js`.

### E2E Tests

```bash
cd front
yarn test:e2e
```

Uses Playwright. Requires both frontend and backend to be running.

## Linting & Formatting

```bash
cd front
yarn lint      # Check formatting + lint
yarn format    # Auto-fix formatting
```

ESLint config supports Svelte files via `eslint-plugin-svelte`.
