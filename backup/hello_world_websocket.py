from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from dotenv import load_dotenv
from os import getenv

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

socketio = SocketIO(app, cors_allowed_origins="*", ping_timeout=60, path='/hello-world')

@socketio.on('connect')
def handle_connect():
    print('Novo cliente conectado')
    socketio.emit('message', 'Luke I am your father')

@socketio.on('message')
def handle_message(msg):
    print(f'Mensagem recebida: {msg}')
    socketio.emit('response', f'They are crawling out of the goddamn walls: {msg}')

@socketio.on('disconnect')
def handle_disconnect():
    print('Cliente desconectado')

if __name__ == '__main__':
    socketio.run(app, debug=getenv("FLASK_ENV") == 'production')
