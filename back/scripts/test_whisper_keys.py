"""
Test script to validate WHISPER (OpenAI) and WHISPER_GROQ API keys.
Generates a short silent audio clip and sends it to each API to verify auth.

Usage:
    python scripts/test_whisper_keys.py
"""

import os
import sys
import subprocess
import tempfile
import json
import http.client
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.utils.config import config

TEMP_FILE = os.path.join(tempfile.gettempdir(), "whisper_test.mp3")


def generate_test_audio():
    """Generate a 1-second silent mp3 using ffmpeg."""
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "anullsrc=r=16000:cl=mono",
        "-t", "1", "-acodec", "libmp3lame", "-q:a", "9",
        TEMP_FILE,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[ERRO] ffmpeg falhou:\n{result.stderr}")
        sys.exit(1)


def multipart_post(host: str, path: str, api_key: str, model: str) -> tuple[int, str]:
    """Send a multipart/form-data POST using stdlib only."""
    boundary = uuid.uuid4().hex

    with open(TEMP_FILE, "rb") as f:
        file_data = f.read()

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="model"\r\n\r\n'
        f"{model}\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="test.mp3"\r\n'
        f"Content-Type: audio/mpeg\r\n\r\n"
    ).encode() + file_data + f"\r\n--{boundary}--\r\n".encode()

    conn = http.client.HTTPSConnection(host, timeout=15)
    conn.request(
        "POST",
        path,
        body=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
    )
    resp = conn.getresponse()
    return resp.status, resp.read().decode()


def test_openai_whisper():
    """Test the WHISPER (OpenAI) key."""
    key = config.WHISPER
    if not key:
        print("[WHISPER]  ⛔ Chave não configurada (.env WHISPER=)")
        return False

    print(f"[WHISPER]  Chave encontrada: {key[:8]}...{key[-4:]}")

    try:
        status, body = multipart_post(
            "api.openai.com", "/v1/audio/transcriptions", key, "whisper-1"
        )
    except Exception as e:
        print(f"[WHISPER]  ❌ Erro de conexão: {e}")
        return False

    if status == 200:
        print("[WHISPER]  ✅ OK — API respondeu com sucesso")
        return True
    else:
        print(f"[WHISPER]  ❌ Falhou ({status}): {body}")
        return False


def test_groq_whisper():
    """Test the WHISPER_GROQ key."""
    key = config.WHISPER_GROQ
    if not key:
        print("[GROQ]     ⛔ Chave não configurada (.env WHISPER_GROQ=)")
        return False

    print(f"[GROQ]     Chave encontrada: {key[:8]}...{key[-4:]}")

    try:
        status, body = multipart_post(
            "api.groq.com", "/openai/v1/audio/transcriptions", key, "whisper-large-v3-turbo"
        )
    except Exception as e:
        print(f"[GROQ]     ❌ Erro de conexão: {e}")
        return False

    if status == 200:
        print("[GROQ]     ✅ OK — API respondeu com sucesso")
        return True
    else:
        print(f"[GROQ]     ❌ Falhou ({status}): {body}")
        return False


def main():
    print("=" * 50)
    print("  Teste de chaves Whisper")
    print("=" * 50)
    print()

    print("Gerando áudio de teste (1s silêncio)...")
    generate_test_audio()
    print()

    ok_openai = test_openai_whisper()
    print()
    ok_groq = test_groq_whisper()
    print()

    print("=" * 50)
    print(f"  OpenAI Whisper: {'✅' if ok_openai else '❌'}")
    print(f"  Groq Whisper:   {'✅' if ok_groq else '❌'}")
    print("=" * 50)

    # cleanup
    if os.path.exists(TEMP_FILE):
        os.remove(TEMP_FILE)


if __name__ == "__main__":
    main()
