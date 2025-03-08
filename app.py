# macaco adesivo gevent pra infra
from gevent import monkey
monkey.patch_all()

from asyncio import new_event_loop, set_event_loop
from typing import Awaitable, Callable, TypeVar
from flask import Flask, request, jsonify, Response
from flask_socketio import SocketIO
from os import getenv
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

from print_page import print_page
from process_convo import process_convo

load_dotenv(override=True)
prod = getenv("FLASK_ENV")

app = Flask(__name__)
MEGABYTE = (2 ** 10) ** 2
app.config['MAX_CONTENT_LENGTH'] = None
# Max number of fields in a multi part form (I don't send more than one file)
# app.config['MAX_FORM_PARTS'] = ...
app.config['MAX_FORM_MEMORY_SIZE'] = 50 * MEGABYTE

cors_origins=[
    "https://whatsorganizer.com.br",
    "https://www.whatsorganizer.com.br",
    "http://localhost:5173"
    ]

# CORS(app, resources={ "/*": { "origins": cors_origins } })

rmq_url = f"amqp://{getenv('RMQ_HOST')}:{getenv('RMQ_PORT')}"
socketio = SocketIO(app,
                    cors_allowed_origins=cors_origins,
                    ping_timeout=80,
                    async_mode='gevent' if prod else None,
                    message_queue=rmq_url if prod else None)
executor = ThreadPoolExecutor()

@socketio.on('connect')
def handle_connect():
    socketio.emit('Smessage', {'data': 'Enviando Arquivo...'})

sock_send: Callable[[str], None] = lambda msg: socketio.emit('Smessage', {'data': msg})

executor = ThreadPoolExecutor()
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
    file = request.files.get('file')
    if not file:
        return jsonify({'Erro': 'Erro ao Obter Anexos'}), 400
    
    pdf_bytes = executor.submit(run_async, print_page(file, sock_send)).result()
    
    return Response(
        pdf_bytes,
        mimetype='application/pdf',
        headers={
            'Content-Disposition': 'attachment; filename="document.pdf"'
        }
    )

@app.route('/process', methods=['POST'])
def process_zip():
    sock_send("Iniciando Processamento...")
    if 'file' not in request.files:
        return jsonify({"Erro": "Arquivo Não Encontrado"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"Erro": "Nome do Arquivo Incompatível"}), 400
    
    if not (file and file.filename.endswith('.zip')):
        return jsonify({"Erro": "Invalid file format"}), 400
    
    return process_convo(file, sock_send)