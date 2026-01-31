"""
API Key authentication decorator.
- If API_KEYS env var is not set, all requests are allowed (backwards compatible).
- Requests from the frontend origin bypass auth.
- External consumers must send X-API-Key header.
"""
from functools import wraps
from os import getenv
from flask import request, jsonify


ALLOWED_ORIGINS = [
    "https://whatsorganizer.com.br",
    "https://www.whatsorganizer.com.br",
]


def _get_api_keys():
    raw = getenv("API_KEYS", "")
    if not raw:
        return None
    return [k.strip() for k in raw.split(",") if k.strip()]


def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        keys = _get_api_keys()
        # No keys configured = open access (backwards compatible)
        if keys is None:
            return f(*args, **kwargs)

        # Frontend origin bypass
        origin = request.headers.get("Origin", "")
        if origin in ALLOWED_ORIGINS:
            return f(*args, **kwargs)

        # Check API key header
        provided_key = request.headers.get("X-API-Key", "")
        if provided_key and provided_key in keys:
            return f(*args, **kwargs)

        return jsonify({"Erro": "API key missing or invalid"}), 401

    return decorated
