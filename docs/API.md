# API Reference

Base URL: `https://api.whatsorganizer.com.br` (production) | `http://localhost:3000` (development)

## Authentication

- **Frontend** (whatsorganizer.com.br): Bypasses auth via `Origin` header
- **External consumers**: Must include `X-API-Key` header
- **No `API_KEYS` configured**: All requests are allowed (backwards compatible)

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| `POST /process` | 10 requests/minute |
| `POST /download-pdf` | 20 requests/minute |
| `GET /health` | No limit |
| `GET /api/info` | No limit |
| `GET /media/:filename` | No limit |

Rate limit exceeded returns `429 Too Many Requests`.

---

## Endpoints

### `GET /health`

Health check endpoint.

**Response** `200`
```json
{
  "status": "healthy",
  "version": "2.0-refactored"
}
```

---

### `GET /api/info`

API metadata and available endpoints.

**Response** `200`
```json
{
  "name": "WhatsApp Organizer API",
  "version": "2.0",
  "description": "Refactored WhatsApp conversation processor with modular architecture",
  "endpoints": {
    "/process": "Process WhatsApp ZIP files",
    "/download-pdf": "Download PDF attachments",
    "/media/<path:filename>": "Serve media files (PDF images, etc.)",
    "/health": "Health check",
    "/api/info": "API information"
  }
}
```

---

### `POST /process`

Process a WhatsApp exported ZIP file.

**Headers**
```
X-API-Key: <your-key>  (required for external consumers)
```

**Query Parameters**
| Param | Type | Description |
|-------|------|-------------|
| `uid` | string | Unique session identifier |

**Body**: `multipart/form-data`
| Field | Type | Description |
|-------|------|-------------|
| `file` | File | `.zip` file exported from WhatsApp |

**Response** `200` — Array of message objects:
```json
[
  {
    "ID": 1,
    "Name": "John",
    "Date": "01/01/2025",
    "Time": "10:00",
    "Message": "Hello!",
    "FileAttached": false,
    "IsApple": false
  },
  {
    "ID": 2,
    "Name": "Jane",
    "Date": "01/01/2025",
    "Time": "10:01",
    "Message": "",
    "FileAttached": "photo.jpg",
    "IsApple": false
  }
]
```

**Error responses**:
- `400` — Missing file, invalid filename, or non-ZIP file
- `401` — API key missing or invalid
- `429` — Rate limit exceeded

---

### `POST /download-pdf`

Generate a PDF document from processed chat messages.

**Headers**
```
Content-Type: application/json
X-API-Key: <your-key>  (required for external consumers)
```

**Body**:
```json
{
  "messages": [
    {
      "ID": 1,
      "Name": "John",
      "Date": "01/01/2025",
      "Time": "10:00",
      "Message": "Hello!",
      "FileAttached": false,
      "IsApple": false
    }
  ],
  "isApple": false
}
```

**Response** `200` — Binary PDF file with header:
```
Content-Disposition: attachment; filename="document.pdf"
Content-Type: application/pdf
```

**Error responses**:
- `400` — Missing messages data
- `401` — API key missing or invalid
- `429` — Rate limit exceeded
- `500` — PDF generation error

---

### `GET /media/:filename`

Serve media files from processing directories.

**Path Parameters**
| Param | Type | Description |
|-------|------|-------------|
| `filename` | string | Name of the media file |

**Response** `200` — Binary file with appropriate MIME type:
- `.pdf` → `application/pdf`
- `.png`, `.jpg`, `.jpeg` → `image/png`
- `.mp3`, `.opus` → `audio/mpeg`
- Other → auto-detected

**Error responses**:
- `403` — Directory traversal attempt
- `404` — File not found

## WebSocket Events

Connection URL: same as API base URL.

**Query**: `uid=<session-uuid>`

| Event | Direction | Description |
|-------|-----------|-------------|
| `connect` | server → client | Emits `Smessage` with "Enviando Arquivo..." |
| `Smessage` | server → client | Progress updates: `{ data: "message" }` |
| `disconnect` | client → server | Triggers LGPD file cleanup |
| `error` | — | Triggers LGPD file cleanup |
