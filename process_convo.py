import uuid
import json
import os
import shutil
from typing import Callable, Mapping, List, Tuple, TypeAlias, Union

from handle_zip_file import handle_zip_file
from list_files import list_files_in_directory
from find_whats_key_data import find_whats_key
from extract_device import extract_info_device, Mobile
from file_fixer import process_file_fixer 
from extract_objects import extract_info_iphone, extract_info_android, TMessageData
from converter_mp3 import convert_opus_to_mp3
from converter_pdf import process_pdf_folder
from file_append import file_appending, file_appending_pdf
from flask.app import Response
from flask.json import jsonify
from werkzeug.datastructures import FileStorage

JsonResp: TypeAlias = Union[Tuple[Response, int], Response]

def process_convo(file: FileStorage, notify_callback: Callable[[str], None]) -> JsonResp:
    # Create a unique working directory
    base_folder = "./zip_tests/"
    unique_folder_name = str(uuid.uuid4())
    final_work_folder = os.path.join(base_folder, unique_folder_name)
    os.makedirs(final_work_folder, exist_ok=True)
    
    # Save the uploaded file
    notify_callback('Recebendo Arquivo zip...')
    zip_path = os.path.join(final_work_folder, "uploaded.zip")
    file.save(zip_path)
    
    # Process the zip file
    notify_callback('Criando Pastas Provisórias...')
    handle_zip_file(zip_path, final_work_folder)
    
    # List objects in the directory
    notify_callback('Coletando Arquivos da Conversa...')
    file_obj_list = list_files_in_directory(final_work_folder)

    # Convert MP3 and transcribe
    notify_callback('Convertendo MP3 e Transcrevendo Áudios...')
    transcriptions = convert_opus_to_mp3(final_work_folder)

    # Transform PDF into Images 
    notify_callback('Trabalhando com PDFs e Office...')
    print("Converter PDF, transformar em imagens e links")
    # bucket_name = 'tempfilesprocessing'
    pdf_img_links = process_pdf_folder(final_work_folder)

    # Extract main conversation
    whats_main_file = find_whats_key(file_obj_list)
    whats_main_folder_file = os.path.join(final_work_folder, whats_main_file)
    
    # Extract device info
    notify_callback('Extraindo Informações do Dispositivo...')
    extract: Mapping[
        Mobile,
        Callable[[], List[TMessageData]]
    ] = {
        "android": lambda: extract_info_android(fixed_file, attached_files),
        "iphone": lambda: extract_info_iphone(fixed_file, attached_files),
    }

    dispositivo = extract_info_device(whats_main_folder_file)
    
    if dispositivo not in extract.keys():
        return jsonify({"Erro": "Dispositivo desconhecido"}), 400
    
    # Fix files
    fixed_file = process_file_fixer(whats_main_folder_file, dispositivo)
    
    attached_files: Tuple[str] = tuple(obj['name'] for obj in file_obj_list if obj.get('name'))
    
    # Extract info based on device type
    
    notify_extract: Callable[
        [Mobile],
    None] = lambda device: notify_callback(f'{device.title()} detectado!')
    
    notify_extract(dispositivo)
    notify_callback('Processando Arquivos e Mídia...')
    extracted_info = extract[dispositivo]()
    
    # Append files
    list_files = file_appending(extracted_info, transcriptions)
    list_files_pdf = file_appending_pdf(extracted_info, pdf_img_links)
    notify_callback('Organizando Mensagens...')

    # Create JSON output
    output_path = os.path.join(final_work_folder, 'output.json')
    with open(output_path, 'w') as f:
        json.dump(list_files, f)
    
    # Read the JSON file and return its contents
    with open(output_path, 'r') as f:
        result = json.load(f)
    
    print("????")
    # print(result)
    # print(jsonify(result))
    if os.path.exists(final_work_folder):
        try:
            # Delete the folder and all its contents
            shutil.rmtree(final_work_folder)
            print(f"Successfully deleted folder: {final_work_folder}")
        except Exception as e:
            print(f"Error deleting folder: {e}")
    else:
        print(f"Folder does not exist: {final_work_folder}")
    
    notify_callback('Processamento Finalizado!')
    return jsonify(result)
