# Architecture

## System Overview

WhatsApp Organizer is a monorepo with three main components:

```
whats-organizer/
├── back/          # Flask API (Python)
├── front/         # SvelteKit SPA (JavaScript)
├── infra/         # Deployment & infrastructure
└── tests/         # Test fixtures
```

### Backend (`back/`)

Flask application with WebSocket support via Flask-SocketIO. Runs behind Gunicorn with gevent workers in production; uses RabbitMQ as message queue for multi-process WebSocket coordination.

```
back/
├── app.py                    # Flask entry point, route definitions
├── api/
│   └── whatsapp_api.py       # Main API interface for ZIP processing
├── src/
│   ├── core/                 # Business logic
│   │   ├── zip_extractor.py        # ZIP file extraction & validation
│   │   ├── zip_analyzer.py         # ZIP content analysis
│   │   ├── audit_zip.py            # Security audit (malware detection)
│   │   ├── message_extractor.py    # WhatsApp message parsing
│   │   ├── conversation_processor.py # Conversation orchestration
│   │   └── media_processor.py      # Media file handling
│   ├── models/               # Pydantic data models
│   │   ├── device.py               # Device detection (iOS/Android)
│   │   ├── message.py              # Message model
│   │   └── zip_analysis.py         # ZIP analysis result model
│   ├── utils/                # Utilities
│   │   ├── auth.py                 # API key authentication
│   │   ├── generate_pdf_weasyprint.py # PDF generation (WeasyPrint + Jinja2)
│   │   ├── connection_handlers.py  # WebSocket connect/disconnect + LGPD cleanup
│   │   ├── converter_mp3.py        # Audio conversion
│   │   ├── converter_pdf.py        # PDF conversion utilities
│   │   ├── sanitize.py             # Input sanitization
│   │   ├── config.py               # Configuration management
│   │   ├── globals.py              # Global state (task tracking)
│   │   └── file_utils.py           # File operation helpers
│   └── templates/            # Jinja2 HTML templates for PDF output
└── requirements.txt
```

### Frontend (`front/`)

SvelteKit single-page application. Communicates with the backend via REST API and Socket.IO for real-time progress updates.

```
front/src/
├── routes/
│   ├── +page.svelte                # Home page (renders Main component)
│   ├── +layout.svelte              # Root layout
│   ├── sitemap.xml/+server.js      # Dynamic sitemap
│   └── robots.txt/+server.js       # Robots.txt
├── lib/
│   ├── Main.svelte                 # Primary application component (~1,660 lines)
│   ├── UploadButton.svelte         # Drag & drop file upload
│   ├── Toast.svelte                # Toast notification system
│   ├── ChatComponents/
│   │   ├── Audio.svelte            # WhatsApp-styled audio player
│   │   └── Video.svelte            # Video player with thumbnail
│   ├── CloseSvg.svelte             # Close icon
│   ├── ErrorSvg.svelte             # Error icon
│   ├── PrinterSvg.svelte           # Printer icon
│   ├── TranscribeSvg.svelte        # Transcription icon
│   ├── UploadIcon.svelte           # Upload icon
│   └── types/
│       └── toast.type.js           # Toast type definitions
└── app.html                        # HTML shell (includes GA4)
```

## Data Flow

1. **Upload**: User uploads a `.zip` file exported from WhatsApp
2. **Processing**: Backend extracts ZIP, parses chat text, detects device type (iOS/Android)
3. **Security audit**: Checks for malicious files (.exe, .bat, .sh, .dll)
4. **Media handling**: Identifies images, videos, audio, PDFs, and Word documents
5. **Response**: Returns structured JSON array of messages with metadata
6. **Client-side enrichment**: Frontend opens ZIP locally, creates object URLs for media
7. **PDF generation**: On request, backend generates a PDF from messages using WeasyPrint + Jinja2 templates
8. **Cleanup**: LGPD-compliant automatic deletion of all user files on disconnect

## Key Design Decisions

- **WeasyPrint over Playwright**: PDF generation uses WeasyPrint + Jinja2 instead of headless browsers, reducing resource usage and system dependencies
- **Client-side ZIP processing**: Media files are extracted and displayed client-side via `JSZip`, reducing server bandwidth
- **Gevent async**: Production uses gevent for cooperative multitasking with Flask-SocketIO
- **RabbitMQ**: Multi-process WebSocket coordination in production (Gunicorn workers)
- **LGPD compliance**: All personal files are destroyed on WebSocket disconnect/error
