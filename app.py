"""
New Flask application using the refactored WhatsApp processor
Maintains API compatibility while using the new modular system
"""
# Gevent monkey patching for infrastructure - MUST be first
from gevent import monkey
monkey.patch_all()

from backend.utils.connection_handlers import handle_disconnect, handle_connect

from asyncio import new_event_loop, set_event_loop
from typing import Awaitable, Callable, TypeVar
from flask import Flask, request, jsonify, send_file, abort, app
from flask_socketio import SocketIO
from flask_cors import CORS
from os import getenv, path
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4
from backend.utils.globals import globals
import os

from api.whatsapp_api import create_whatsapp_api

from backend.utils.print_page_pdf import print_page_pdf

load_dotenv(override=True)

prod_env = getenv("FLASK_ENV")
port_env = getenv("FLASK_PORT")
host_env = getenv("HOST")

prod = (prod_env or "").lower() in ("prod", "production") 
port = int(port_env or 5000)
host = host_env or "0.0.0.0"

app = Flask(__name__)
MEGABYTE = (2 ** 10) ** 2
app.config['MAX_CONTENT_LENGTH'] = None
app.config['MAX_FORM_MEMORY_SIZE'] = 50 * MEGABYTE

cors_origins = [
    "https://whatsorganizer.com.br",
    "https://www.whatsorganizer.com.br",
    *([
    "http://localhost:5173",
    "http://localhost:1337"
    ] if not prod else [])
]

# Enable CORS for the Flask app
CORS(app, resources={"/*": {"origins": cors_origins}})

rmq_url = f"amqp://{getenv('RMQ_HOST')}:{getenv('RMQ_PORT')}"
socketio = SocketIO(
    app,
    cors_allowed_origins=cors_origins,
    ping_timeout=80,
    async_mode='gevent' if prod else None,
    message_queue=rmq_url if prod else None
)

executor = ThreadPoolExecutor()

# Initialize new API
whatsapp_api = create_whatsapp_api()

@socketio.on('connect')
def on_connect():
    socketio.emit('Smessage', {'data': 'Enviando Arquivo...'})
    handle_connect()

@socketio.on('disconnect')
def on_disconnect():
    """
    Deletes all PERSONAL FILES LGPD (Most companies would sell this data for $)
    """
    handle_disconnect()

@socketio.on('error')
def on_error():
    """
    Deletes all PERSONAL FILES LGPD (Most companies would sell this data for $)
    """
    handle_disconnect()

sock_send: Callable[[str], None] = lambda msg: socketio.emit('Smessage', {'data': msg})

def run_async(coroutine):
    """Executa uma corotina assíncrona em uma nova thread com seu próprio loop de eventos."""
    loop = new_event_loop()
    set_event_loop(loop)
    try:
        return loop.run_until_complete(coroutine)
    finally:
        loop.close()

T = TypeVar('T')
def run_coroutine_sync(coro: Awaitable[T]) -> T:
    """ Creates a new event loop to run asynchronous operations in a threaded environment """
    loop = new_event_loop()
    set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

@app.route('/download-pdf', methods=['POST'])
def download_pdf():
    """Legacy PDF download endpoint - keep for compatibility"""
    file = request.files.get('file')
    if not file:
        return jsonify({'Erro': 'Erro ao Obter Anexos'}), 400
    
    from flask import Response
    pdf_bytes = executor.submit(run_async, print_page_pdf(file, sock_send)).result()
    
    return Response(
        pdf_bytes,
        mimetype='application/pdf',
        headers={
            'Content-Disposition': 'attachment; filename="document.pdf"'
        }
    )

@app.route('/process', methods=['POST'])
def process_zip():
    """
    Main processing endpoint using new modular system
    Maintains compatibility with existing frontend
    """
    sock_send("Iniciando Processamento...")
    
    if 'file' not in request.files:
        return jsonify({"Erro": "Arquivo Não Encontrado"}), 400
    
    file = request.files['file']
    uid = request.args.get('uid')
    
    if not file.filename:
        return jsonify({"Erro": "Nome do Arquivo Incompatível"}), 400
    
    if not (file and file.filename.endswith('.zip')):
        return jsonify({"Erro": "Invalid file format"}), 400
    
    task_id = str(uid)
    globals.create_task(task_id)

    # Use new API with progress callback
    return whatsapp_api.process_zip_file(file, task_id, sock_send)

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
    print("🚀 Starting WhatsApp Organizer API v2.0 (Refactored)")
    print("📁 Using local file storage (no AWS dependency)")
    print("🧹 LGPD compliant with automatic file cleanup")
    
    # Test API initialization
    try:
        test_api = create_whatsapp_api()
        print("✅ API initialization successful")
    except Exception as e:
        print(f"❌ API initialization failed: {e}")
        import traceback
        traceback.print_exc()
    
    if prod:
        print("🌐 Production mode with RabbitMQ")
        socketio.run(app, host=host, port=int(port or 5000))
    else:
        print("🔧 Development mode")
        app.run(host=host, port=int(port or 5000), debug=True)
