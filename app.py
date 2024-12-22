from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
import uuid
import json
import os
import shutil

# Import your existing functions
from handle_zip_file import handle_zip_file
from list_files import list_files_in_directory
from find_whats_key_data import find_whats_key
from extract_device import extract_info_device
from file_fixer import process_file_fixer 
from extract_objects_v2 import extract_info_iphone, extract_info_android
from converter_mp3 import convert_opus_to_mp3
from converter_pdf import process_pdf_folder
from file_append import file_appending, file_appending_pdf
from dotenv import load_dotenv

load_dotenv()
prod = os.getenv("FLASK_ENV")

app = Flask(__name__)

cors_origins=[
    "https://whatsorganizer.com.br",
    "https://www.whatsorganizer.com.br",
    "http://localhost:5173"
    ]

# CORS(app, resources={ "/*": { "origins": cors_origins } })

rmq_url = f"amqp://{os.getenv('RMQ_HOST')}:{os.getenv('RMQ_PORT')}"
socketio = SocketIO(app,
                    cors_allowed_origins=cors_origins,
                    ping_timeout=60,
                    async_mode='gevent',
                    message_queue=rmq_url)


@socketio.on('connect')
def handle_connect():
    socketio.emit('Smessage', {'data': 'Enviando Arquivo...'})


@app.route('/process', methods=['POST'])
def process_zip():
    socketio.emit('Smessage', { 'data': "Iniciando Processamento..."})
    if 'file' not in request.files:
        return jsonify({"Erro": "Arquivo Não Encontrado"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"Erro": "Nome do Arquivo Incompatível"}), 400
    
    if file and file.filename.endswith('.zip'):
        # Create a unique working directory
        base_folder = "./zip_tests/"
        unique_folder_name = str(uuid.uuid4())
        final_work_folder = os.path.join(base_folder, unique_folder_name)
        os.makedirs(final_work_folder, exist_ok=True)
                
        # Save the uploaded file
        zip_path = os.path.join(final_work_folder, "uploaded.zip")
        file.save(zip_path)
        socketio.emit('Smessage', {'data': 'Arquivo Salvo com Sucesso!'})
        
        # Process the zip file
        handle_zip_file(zip_path, final_work_folder)
        socketio.emit('Smessage', {'data': 'Criando Pastas Provisórias...'})
        
        # List objects in the directory
        file_object = list_files_in_directory(final_work_folder)
        socketio.emit('Smessage', {'data': 'Coletando Arquivos da Conversa...'})
        
        # Convert MP3 and transcribe
        transcriptions = convert_opus_to_mp3(final_work_folder)
        socketio.emit('Smessage', {'data': 'Convertendo MP3 e Transcrevendo Áudios...'})
        
        # Transform PDF into Images 
        print("Converter PDF, transformar em imagens e links")
        bucket_name = 'tempfilesprocessing'
        pdf_img_links = process_pdf_folder(final_work_folder, bucket_name)
        socketio.emit('Smessage', {'data': 'Trabalhando com PDFs e DOCXs...'})

        # Extract main conversation
        whats_main_file = find_whats_key(file_object)
        whats_main_folder_file = os.path.join(final_work_folder, whats_main_file)
        
        # Extract device info
        dispositivo = extract_info_device(whats_main_folder_file)
        socketio.emit('Smessage', {'data': 'Extraindo Informações do Dispositivo...'})
        
        # Fix files
        fixed_file = process_file_fixer(whats_main_folder_file, dispositivo)
        
        # Extract info based on device type
        if dispositivo == "android":
            extracted_info = extract_info_android(fixed_file)
            socketio.emit('Smessage', {'data': 'Android Detectado!'})
        elif dispositivo == "iphone":
            extracted_info = extract_info_iphone(fixed_file)
            socketio.emit('Smessage', {'data': 'Iphone Detectado!'})
        else:
            return jsonify({"error": "Unknown device type"}), 400
        
        # Append files
        list_files = file_appending(extracted_info, transcriptions)
        lit_files_pdf = file_appending_pdf(extracted_info, pdf_img_links)
        socketio.emit('Smessage', {'data': 'Organizando Mensagens...'})

        print(extracted_info)
        print(type(extracted_info))

        # Create JSON output
        output_path = os.path.join(final_work_folder, 'output.json')
        with open(output_path, 'w') as f:
            json.dump(list_files, f)
        
        # Read the JSON file and return its contents
        with open(output_path, 'r') as f:
            result = json.load(f)
        
        print("????")
        print(result)
        print(jsonify(result))
        if os.path.exists(final_work_folder):
            try:
                # Delete the folder and all its contents
                shutil.rmtree(final_work_folder)
                print(f"Successfully deleted folder: {final_work_folder}")
            except Exception as e:
                print(f"Error deleting folder: {e}")
        else:
            print(f"Folder does not exist: {final_work_folder}")
    
        socketio.emit('Smessage', {'data': 'Processamento Finalizado!'})
        return jsonify(result)
        
    return jsonify({"error": "Invalid file format"}), 400


if __name__ == '__main__':
    print('main')
    socketio.run(app, debug=os.getenv("FLASK_ENV") == 'production')
