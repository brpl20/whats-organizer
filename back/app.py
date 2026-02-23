"""
New Flask application using the refactored WhatsApp processor
Maintains API compatibility while using the new modular system
----
"""
import json
import queue
import threading
import tempfile
import time
import shutil

from flask import Flask, request, jsonify, send_file, abort, Response, stream_with_context
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from src.utils.auth import require_api_key
from os import getenv, path
from dotenv import load_dotenv
import os

from api.whatsapp_api import create_whatsapp_api, WhatsAppAPI
from src.utils.generate_pdf_weasyprint import generate_pdf

port_env = getenv("FLASK_PORT")
load_dotenv(override=True)

prod_env = getenv("FLASK_ENV")
port_env = port_env or getenv("FLASK_PORT")
host_env = getenv("HOST")
max_upload_mb_env = getenv("PUBLIC_MAX_UPLOAD_MB")

prod = (prod_env or "").lower() in ("prod", "production")
port = int(port_env or 5000)
host = host_env or "0.0.0.0"

app = Flask(__name__)
MEGABYTE = (2 ** 10) ** 2
app.config['MAX_CONTENT_LENGTH'] = None
app.config['MAX_FORM_MEMORY_SIZE'] = int(max_upload_mb_env or 100) * MEGABYTE

cors_origins = [
    "https://whatsorganizer.com.br",
    "https://www.whatsorganizer.com.br",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:1337"
]

# Enable CORS for the Flask app
CORS(app, resources={"/*": {"origins": cors_origins}})

# Rate limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://",
)

# Initialize new API
whatsapp_api: WhatsAppAPI

try:
    whatsapp_api = create_whatsapp_api()
    print("API initialization successful")
except Exception as e:
    print(f"API initialization failed: {e}")
    import traceback
    traceback.print_exc()


def _ttl_cleanup():
    """Background daemon that deletes zip_tests/ folders older than 1 hour every 10 minutes"""
    base = "./zip_tests/"
    while True:
        time.sleep(600)  # 10 minutes
        try:
            if not os.path.isdir(base):
                continue
            now = time.time()
            for entry in os.listdir(base):
                entry_path = os.path.join(base, entry)
                if os.path.isdir(entry_path):
                    age = now - os.path.getmtime(entry_path)
                    if age > 3600:  # 1 hour
                        shutil.rmtree(entry_path, ignore_errors=True)
                        print(f"TTL cleanup: removed {entry_path}")
        except Exception as e:
            print(f"TTL cleanup error: {e}")

_cleanup_thread = threading.Thread(target=_ttl_cleanup, daemon=True)
_cleanup_thread.start()


@app.route('/download-pdf', methods=['POST'])
@limiter.limit("20/minute")
@require_api_key
def download_pdf():
    """Generate PDF from chat messages using WeasyPrint"""
    data = request.get_json(silent=True)
    if not data or 'messages' not in data:
        return jsonify({'Erro': 'Dados de mensagens nao encontrados'}), 400

    messages = data['messages']
    is_apple = bool(data.get('isApple', False))

    try:
        pdf_bytes = generate_pdf(messages, is_apple, lambda msg: None)
    except Exception as e:
        print(f"PDF generation error: {e}")
        return jsonify({'Erro': 'Erro ao gerar o PDF'}), 500

    return Response(
        pdf_bytes,
        mimetype='application/pdf',
        headers={
            'Content-Disposition': 'attachment; filename="document.pdf"'
        }
    )

@app.route('/process', methods=['POST'])
@limiter.limit("10/minute")
@require_api_key
def process_zip():
    """
    Main processing endpoint using SSE streaming
    Maintains compatibility with existing frontend
    """
    if 'file' not in request.files:
        return jsonify({"Erro": "Arquivo Nao Encontrado"}), 400

    file = request.files['file']

    if not file.filename:
        return jsonify({"Erro": "Nome do Arquivo Incompativel"}), 400

    if not (file and file.filename.endswith('.zip')):
        return jsonify({"Erro": "Arquivo invalido"}), 400

    # Save file to a temp location BEFORE streaming starts (request context won't be available in bg thread)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
    try:
        file.save(tmp)
        tmp_path = tmp.name
    finally:
        tmp.close()

    q = queue.Queue()

    def notify(msg):
        q.put(('progress', msg))

    def background():
        working_folder = None
        try:
            result = whatsapp_api.process_zip_file(tmp_path, notify)
            working_folder = result.pop('_working_folder', None)
            if 'Erro' in result:
                q.put(('error', result))
            else:
                q.put(('result', result.get('resultado', [])))
        except Exception as e:
            q.put(('error', {"Erro": str(e)}))
        finally:
            q.put(('done', None))
            # LGPD cleanup
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            if working_folder and os.path.isdir(working_folder):
                shutil.rmtree(working_folder, ignore_errors=True)

    t = threading.Thread(target=background, daemon=True)
    t.start()

    def generate():
        while True:
            try:
                kind, data = q.get(timeout=600)  # 10 min max
            except queue.Empty:
                yield f"event: error\ndata: {json.dumps({'Erro': 'Timeout no processamento'})}\n\n"
                break

            if kind == 'progress':
                yield f"event: progress\ndata: {json.dumps({'message': data})}\n\n"
            elif kind == 'result':
                yield f"event: result\ndata: {json.dumps(data)}\n\n"
                break
            elif kind == 'error':
                yield f"event: error\ndata: {json.dumps(data)}\n\n"
                break
            elif kind == 'done':
                break

    return Response(stream_with_context(generate()), mimetype='text/event-stream',
                    headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "version": "2.0-refactored"}), 200

@app.route('/api/info', methods=['GET'])
def api_info():
    """API information endpoint"""
    return jsonify({
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
    }), 200

@app.route('/media/<path:filename>')
def serve_media(filename):
    """
    Serve media files (PDF images, audio files, PDF documents, etc.) from zip_tests directory
    """
    try:
        # Security: prevent directory traversal
        if '..' in filename or filename.startswith('/'):
            abort(403)

        # Search for the file in all zip_tests subdirectories
        base_dir = "./zip_tests/"

        # Look for the file in all processing directories
        for root, dirs, files in os.walk(base_dir):
            file_path = os.path.join(root, filename)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                # Determine appropriate mimetype
                if filename.lower().endswith('.pdf'):
                    return send_file(file_path, mimetype='application/pdf')
                elif filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    return send_file(file_path, mimetype='image/png')
                elif filename.lower().endswith(('.mp3', '.opus')):
                    return send_file(file_path, mimetype='audio/mpeg')
                else:
                    return send_file(file_path)

        # If not found, return 404
        abort(404)

    except Exception as e:
        print(f"Error serving media file {filename}: {e}")
        abort(404)

if __name__ == '__main__':
    print("Starting WhatsApp Organizer API v2.0 (Refactored)")
    print("Using local file storage (no AWS dependency)")
    print("LGPD compliant with automatic file cleanup")
    app.run(host=host, port=int(port or 5000), debug=not prod)
