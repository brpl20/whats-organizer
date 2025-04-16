# NEW CONVO 
import uuid
import json
import os
import shutil
from typing import Callable, Dict, List, Optional, Tuple, TypeAlias, Union, Any, Mapping

# Import the zip_analyser functions
from zip_analyser import analyze_zip_file, MAX_EXTRACTED_SIZE, MAX_COMPRESSION_RATIO, MAX_FILES
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

# Define a type for storing ZIP analysis data
ZipAnalysisData = Dict[str, Any]

JsonResp: TypeAlias = Union[Tuple[Response, int], Response]

def process_convo(file: FileStorage, unique_folder_name: str, notify_callback: Callable[[str], None]) -> JsonResp:
    # Create a unique working directory
    base_folder = "./zip_tests/"
    final_work_folder = os.path.join(base_folder, unique_folder_name)
    os.makedirs(final_work_folder, exist_ok=True)
    
    # Storage for ZIP analysis results
    zip_analysis_data: ZipAnalysisData = {}
        
    # Save the uploaded file
    notify_callback('Recebendo Arquivo zip...')
    zip_path = os.path.join(final_work_folder, "uploaded.zip")
    file.save(zip_path)
     
    # Run ZIP analysis
    # Check file size before processing
    notify_callback('Analisando arquivo ZIP para segurança...')
    file_size = os.path.getsize(zip_path)
    if file_size > MAX_EXTRACTED_SIZE:
        return jsonify({"Erro": f"Arquivo muito grande: {file_size} bytes. Máximo permitido: {MAX_EXTRACTED_SIZE} bytes."}), 400
    detected_device = None  # Default to None
    whatsapp_contact = None
    
    try:
        analysis_result = analyze_zip_file(zip_path)
        
        # Store analysis data
        zip_analysis_data["analysis"] = analysis_result
        
        # Check for ZIP bomb and other security issues
        if "SECURITY ALERT" in analysis_result:
            return jsonify({"Erro": "Possível ameaça de segurança detectada no arquivo ZIP. Por favor, verifique o arquivo."}), 400
        
        # Extract device type from analysis
        system_info = ""
        if "Creation systems:" in analysis_result:
            system_info = analysis_result.split("Creation systems:")[1].split("\n")[0].strip()
        
        # Determine device type based on system info
        if any(sys in system_info for sys in ["MS-DOS", "OS/2", "Windows", "NTFS", "VFAT", "UNIX"]):
            detected_device = "android"
        elif any(sys in system_info for sys in ["Macintosh", "OS X", "Darwin"]):
            detected_device = "iphone"
        else:
            detected_device = "android"
            
        # Extract WhatsApp contact name (for Android)
        if detected_device == "android" and "WhatsApp Contacts Found:" in analysis_result:
            contact_section = analysis_result.split("WhatsApp Contacts Found:")[1].split("\n")[1:]
            for line in contact_section:
                if line.strip().startswith("- "):
                    whatsapp_contact = line.strip()[2:].strip()
                    break
        
        # Store extracted info
        zip_analysis_data["detected_device"] = detected_device
        if whatsapp_contact:
            zip_analysis_data["whatsapp_contact"] = whatsapp_contact
            
        # Check for potentially malicious files
        malicious_patterns = [
            ".sh", ".bat", ".cmd", ".ps1", ".vbs", ".js", ".exe", ".dll", ".so",
            ".sql", ".db", "DROP TABLE", "DELETE FROM", "INSERT INTO", "SELECT ",
            "shell", "exec(", "system(", "eval(", "<script", "<?php"
        ]
        
        file_list_section = analysis_result.split("Detailed File List:")[1] if "Detailed File List:" in analysis_result else ""
        suspicious_files = []
        
        for pattern in malicious_patterns:
            if pattern.lower() in file_list_section.lower():
                suspicious_files.append(pattern)
                
        if suspicious_files:
            return jsonify({"Erro": f"Arquivos potencialmente maliciosos detectados: {', '.join(suspicious_files)}"}), 400
            
    except Exception as e:
        # If ZIP analysis fails, fall back to a default
        detected_device = "android"  # Default device type
        print(f"Warning: ZIP analysis failed: {str(e)}. Using default device type: {detected_device}")
    
    # Process the zip file
    notify_callback('Criando Pastas Provisórias...')
    try:
        handle_zip_file(zip_path, final_work_folder)
    except Exception as e:
        return jsonify({"Erro": f"Erro ao extrair o arquivo ZIP: {str(e)}"}), 500
    
    # List objects in the directory
    notify_callback('Coletando Arquivos da Conversa...')
    try:
        file_obj_list = list_files_in_directory(final_work_folder)
    except Exception as e:
        return jsonify({"Erro": f"Erro ao listar arquivos: {str(e)}"}), 500

    # Convert MP3 and transcribe
    notify_callback('Convertendo MP3 e Transcrevendo Áudios...')
    try:
        transcriptions = convert_opus_to_mp3(final_work_folder)
    except Exception as e:
        return jsonify({"Erro": f"Erro ao converter áudios: {str(e)}"}), 500

    # Transform PDF into Images 
    notify_callback('Trabalhando com PDFs e Office...')
    try:
        pdf_img_links = process_pdf_folder(final_work_folder)
    except Exception as e:
        return jsonify({"Erro": f"Erro ao processar PDFs: {str(e)}"}), 500

    # Extract main conversation
    try:
        whats_main_file = find_whats_key(file_obj_list)
        whats_main_folder_file: str = os.path.join(final_work_folder, whats_main_file)
    except Exception as e:
        return jsonify({"Erro": f"Erro ao encontrar arquivo principal de conversa: {str(e)}"}), 500
    
    # Extract device info - using the detected device from ZIP analysis
    notify_callback('Detectando Modelo do Dispositivo...')
    extract: Mapping[
        Mobile,
        Callable[[str], List[TMessageData]]
    ] = {
        "android": lambda fixed_file: extract_info_android(whatsapp_contact, fixed_file, attached_files),
        "iphone": lambda fixed_file: extract_info_iphone(fixed_file, attached_files),
    }
    
    # Use the device detected from ZIP analysis instead of extract_info_device
    dispositivo = detected_device
    
    if dispositivo not in extract.keys():
        return jsonify({"Erro": "Dispositivo desconhecido"}), 400
    
    # Fix files
    try:
        fixed_file = process_file_fixer(whats_main_folder_file, dispositivo)
        print(f'fixed_file = {fixed_file}')
    except Exception as e:
        return jsonify({"Erro": f"Erro ao processar arquivo: {str(e)}"}), 500
    
    attached_files: Tuple[Optional[str], ...] = tuple(obj['name'] for obj in file_obj_list if obj.get('name'))
        
    # Extract info based on device type
    notify_extract: Callable[
        [Mobile],
    None] = lambda device: notify_callback(f'{device.title()} detectado!')
    
    notify_extract(dispositivo)
    notify_callback('Processando Arquivos e Mídia...')
    
    try:
        extracted_info = extract[dispositivo](fixed_file)
    except Exception as e:
        return jsonify({"Erro": f"Erro ao extrair informações: {str(e)}"}), 500
    
    # Append files
    try:
        list_files = file_appending(extracted_info, transcriptions)
        list_files_pdf = file_appending_pdf(extracted_info, pdf_img_links)
    except Exception as e:
        return jsonify({"Erro": f"Erro ao processar anexos: {str(e)}"}), 500
    
    notify_callback('Organizando Mensagens...')

    # Create JSON output
    output_path = os.path.join(final_work_folder, 'output.json')
    
    try:
        with open(output_path, 'w') as f:
            json.dump(list_files, f)
        
        # Read the JSON file and return its contents
        with open(output_path, 'r') as f:
            result: List[TMessageData] = json.load(f)
    except Exception as e:
        return jsonify({"Erro": f"Erro ao salvar ou ler o resultado: {str(e)}"}), 500
    
    # Add ZIP analysis data to the result if available
    if zip_analysis_data:
        # Store analysis results in a separate file
        analysis_path = os.path.join(final_work_folder, 'analysis.json')
        try:
            with open(analysis_path, 'w') as f:
                json.dump(zip_analysis_data, f)
        except Exception as e:
            print(f"Warning: Could not save analysis data: {str(e)}")
    
    notify_callback('Processamento Finalizado!')
    return jsonify(result)