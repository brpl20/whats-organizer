import uuid
import json
import os
import shutil
import pdb
import logging
from typing import Callable, Mapping, List, Optional, Tuple, TypeAlias, Union

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

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_convo(file_path: str, unique_folder_name: str) -> List[TMessageData]:
    """
    Process a WhatsApp conversation export file offline
    
    Args:
        file_path: Path to the uploaded zip file
        unique_folder_name: Unique name for the working directory
        
    Returns:
        List of processed message data
    """
    # Create a unique working directory
    base_folder = "./zip_tests/"
    final_work_folder = os.path.join(base_folder, unique_folder_name)
    os.makedirs(final_work_folder, exist_ok=True)
    
    logger.info('Fazendo Verificações de Segurança...')
    
    # Save the file to working directory
    logger.info('Recebendo Arquivo zip...')
    zip_path = os.path.join(final_work_folder, "uploaded.zip")
    shutil.copyfile(file_path, zip_path)
    
    # Analyze the zip file
    zip_analysis_data = {}
    analysis_result = analyze_zip_file(zip_path)
    zip_analysis_data["analysis"] = analysis_result
    
    file_count = analysis_result["archive_info"]["file_count"]
    print(f"File count: {file_count}")

    is_zip_bomb = "error" in analysis_result and "ZIP bomb" in analysis_result["error"]
    print(f"Is zip bomb: {is_zip_bomb}")
    
    total_size = analysis_result['file_info']['size_bytes']
    formatted_total_size = analysis_result['file_info']['size_formatted']
    print(f"Total size: {total_size} bytes ({formatted_total_size})")
    
    creation_systems = analysis_result['archive_info']['creation_systems']
    device_type = analysis_result['archive_info']['device_type']
    print(f"Device_type:{device_type}")
    
    # Retirar nome do contato do android direto do arquivo 
    # No iphone retira do arquivo
    contact_android = None
    if device_type == "android":
        contact_list = analysis_result['file_info']['contact']
        if isinstance(contact_list, list):
            contact_android = ", ".join(contact_list)
        else:
            contact_android = str(contact_list)
        
        print(f"Contact: {contact_android}")

    creation_tools = analysis_result['origin_analysis']['creation_tools']
    print(f"Device/System: {creation_systems[0]}")
    print(f"Creation tool: {creation_tools[0]}")

    
    # Process the zip file
    logger.info('Criando Pastas Provisórias...')
    handle_zip_file(zip_path, final_work_folder)
    
    # List objects in the directory
    logger.info('Coletando Arquivos da Conversa...')
    file_obj_list = list_files_in_directory(final_work_folder)

    # Convert MP3 and transcribe
    logger.info('Convertendo MP3 e Transcrevendo Áudios...')
    transcriptions = convert_opus_to_mp3(final_work_folder)

    # Transform PDF into Images 
    logger.info('Trabalhando com PDFs e Office...')
    print("Converter PDF, transformar em imagens e links")
    pdf_img_links = process_pdf_folder(final_work_folder)

    # Extract main conversation
    whats_main_file = find_whats_key(file_obj_list)
    whats_main_folder_file: str = os.path.join(final_work_folder, whats_main_file)
    
    # Extract device info
    logger.info('Detectando Modelo do Dispositivo...')
    dispositivo = extract_info_device(whats_main_folder_file)
    
    extract: Mapping[
        Mobile,
        Callable[[str], List[TMessageData]]
    ] = {
        "android": lambda fixed_file: extract_info_android(fixed_file, attached_files, contact_android),
        "iphone": lambda fixed_file: extract_info_iphone(fixed_file, attached_files),
    }
    
    # "android": lambda fixed_file: extract_info_android(fixed_file, attached_files),
    if dispositivo not in extract.keys():
        logger.error("Erro: Dispositivo desconhecido")
        return []
    
    # Fix files
    fixed_file = process_file_fixer(whats_main_folder_file, dispositivo)
    print(f'fixed_file = {fixed_file}')
    
    attached_files: Tuple[Optional[str], ...] = tuple(obj['name'] for obj in file_obj_list if obj.get('name'))
        
    # Extract info based on device type
    logger.info(f'{dispositivo.title()} detectado!')
    logger.info('Processando Arquivos e Mídia...')
    extracted_info = extract[dispositivo](fixed_file)
    
    # Append files
    list_files = file_appending(extracted_info, transcriptions)
    list_files_pdf = file_appending_pdf(extracted_info, pdf_img_links)
    logger.info('Organizando Mensagens...')

    # Create JSON output
    output_path = os.path.join(final_work_folder, 'output.json')
    with open(output_path, 'w') as f:
        json.dump(list_files, f)
    
    # Read the JSON file and return its contents
    with open(output_path, 'r') as f:
        result: List[TMessageData] = json.load(f)
    
    # Cleanup code (commented out)
    # if os.path.exists(final_work_folder):
    #     try:
    #         # Delete the folder and all its contents
    #         shutil.rmtree(final_work_folder)
    #         print(f"Successfully deleted folder: {final_work_folder}")
    #     except Exception as e:
    #         print(f"Error deleting folder: {e}")
    # else:
    #     print(f"Folder does not exist: {final_work_folder}")
    
    logger.info('Processamento Finalizado!')
    return result

if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_zip_file>")
        sys.exit(1)
        
    zip_file_path = sys.argv[1]
    unique_id = str(uuid.uuid4())
    
    try:
        result = process_convo(zip_file_path, unique_id)
        print(f"Processing complete. Output saved to zip_tests/{unique_id}/output.json")
    except Exception as e:
        logger.error(f"Error processing conversation: {str(e)}")