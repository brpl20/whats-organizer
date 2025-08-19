import uuid
import json
import os
import shutil
from typing import Callable, Dict, List, Optional, Tuple, TypeAlias, Union, Any, Mapping

# Import the zip_analyser functions
try:
    from zip_analyser import analyze_zip_file, MAX_EXTRACTED_SIZE, MAX_COMPRESSION_RATIO, MAX_FILES
    print("✓ zip_analyser importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar zip_analyser: {e}")
    
try:
    from handle_zip_file import handle_zip_file
    print("✓ handle_zip_file importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar handle_zip_file: {e}")

try:
    from list_files import list_files_in_directory
    print("✓ list_files importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar list_files: {e}")
    print("Detalhes do erro:", str(e))
    # Vamos criar uma função temporária de fallback
    def list_files_in_directory(directory):
        """Função de fallback para listar arquivos"""
        files = []
        for root, dirs, file_names in os.walk(directory):
            for file_name in file_names:
                file_path = os.path.join(root, file_name)
                files.append({
                    'name': file_name,
                    'path': file_path,
                    'size': os.path.getsize(file_path)
                })
        return files
    print("✓ Usando função de fallback para list_files_in_directory")

try:
    from find_whats_key_data import find_whats_key
    print("✓ find_whats_key_data importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar find_whats_key_data: {e}")

try:
    from extract_device import extract_info_device, Mobile
    print("✓ extract_device importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar extract_device: {e}")

try:
    from file_fixer import process_file_fixer 
    print("✓ file_fixer importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar file_fixer: {e}")

try:
    from extract_objects import extract_info_iphone, extract_info_android, TMessageData
    print("✓ extract_objects importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar extract_objects: {e}")

try:
    from converter_mp3 import convert_opus_to_mp3
    print("✓ converter_mp3 importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar converter_mp3: {e}")

try:
    from converter_pdf import process_pdf_folder
    print("✓ converter_pdf importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar converter_pdf: {e}")

try:
    from file_append import file_appending, file_appending_pdf
    print("✓ file_append importado com sucesso")
except ImportError as e:
    print(f"❌ Erro ao importar file_append: {e}")

# Define a type for storing ZIP analysis data
ZipAnalysisData = Dict[str, Any]

def process_convo(file_path: str, unique_folder_name: str) -> Dict[str, Any]:
    """
    Processa um arquivo ZIP do WhatsApp de forma offline
    
    Args:
        file_path (str): Caminho absoluto para o arquivo ZIP
        unique_folder_name (str): Nome único para a pasta de trabalho
        
    Returns:
        Dict[str, Any]: Resultado do processamento ou erro
    """
    
    # Verificar se o arquivo existe
    if not os.path.exists(file_path):
        return {"Erro": f"Arquivo não encontrado: {file_path}"}
    
    # Create a unique working directory
    base_folder = "./zip_tests/"
    final_work_folder = os.path.join(base_folder, unique_folder_name)
    os.makedirs(final_work_folder, exist_ok=True)
    
    # Storage for ZIP analysis results
    zip_analysis_data: ZipAnalysisData = {}
        
    # Copy the file to working directory
    # Nome fixo porque o diferenciado esta na pasta
    print('Copiando arquivo ZIP...')
    zip_path = os.path.join(final_work_folder, "uploaded.zip")
    try:
        shutil.copy2(file_path, zip_path)
    except Exception as e:
        return {"Erro": f"Erro ao copiar arquivo: {str(e)}"}
     
    # Run ZIP analysis
    # Check file size before processing
    print('Analisando arquivo ZIP para segurança...')
    file_size = os.path.getsize(zip_path)
    if file_size > MAX_EXTRACTED_SIZE:
        return {"Erro": f"Arquivo muito grande: {file_size} bytes. Máximo permitido: {MAX_EXTRACTED_SIZE} bytes."}
    
    detected_device = None  # Default to None
    whatsapp_contact = None
    
    try:
        analysis_result = analyze_zip_file(zip_path)
        
        # Store analysis data
        zip_analysis_data["analysis"] = analysis_result
        
        # Check for ZIP bomb and other security issues
        if "SECURITY ALERT" in analysis_result:
            return {"Erro": "Possível ameaça de segurança detectada no arquivo ZIP. Por favor, verifique o arquivo."}
        
        # Extract device type from analysis
        system_info = ""
        if "Creation systems:" in analysis_result:
            system_info = analysis_result.split("Creation systems:")[1].split("\n")[0].strip()
            print("---System Info---")
            print(system_info)

        # Determine device type based on system info
        print("---System Device---")
        if any(sys in system_info for sys in ["MS-DOS", "OS/2", "Windows", "NTFS", "VFAT", "UNIX"]):
            detected_device = "android"
            print(detected_device)
        elif any(sys in system_info for sys in ["Macintosh", "OS X", "Darwin"]):
            detected_device = "iphone"
            print(detected_device)
        else:
            detected_device = "android"
            print(detected_device)
            
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
            print("---WhatsAppContact---")
            print(whatsapp_contact)
            
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
            return {"Erro": f"Arquivos potencialmente maliciosos detectados: {', '.join(suspicious_files)}"}
            
    except Exception as e:
        # If ZIP analysis fails, fall back to a default
        detected_device = "android"  # Default device type
        print(f"Aviso: Análise do ZIP falhou: {str(e)}. Usando tipo de dispositivo padrão: {detected_device}")
    
    # Process the zip file
    print('Criando Pastas Provisórias...')
    try:
        handle_zip_file(zip_path, final_work_folder)
    except Exception as e:
        return {"Erro": f"Erro ao extrair o arquivo ZIP: {str(e)}"}
    
    # List objects in the directory
    print('Coletando Arquivos da Conversa...')
    try:
        file_obj_list = list_files_in_directory(final_work_folder)
    except Exception as e:
        return {"Erro": f"Erro ao listar arquivos: {str(e)}"}

    # Convert MP3 and transcribe
    print('Convertendo MP3 e Transcrevendo Áudios...')
    try:
        transcriptions = convert_opus_to_mp3(final_work_folder)
    except Exception as e:
        return {"Erro": f"Erro ao converter áudios: {str(e)}"}

    # Transform PDF into Images 
    print('Trabalhando com PDFs e Office...')
    try:
        pdf_img_links = process_pdf_folder(final_work_folder)
    except Exception as e:
        return {"Erro": f"Erro ao processar PDFs: {str(e)}"}

    # Extract main conversation
    try:
        whats_main_file = find_whats_key(file_obj_list)
        whats_main_folder_file: str = os.path.join(final_work_folder, whats_main_file)
    except Exception as e:
        return {"Erro": f"Erro ao encontrar arquivo principal de conversa: {str(e)}"}
    
    # Extract device info - using the detected device from ZIP analysis
    print('Detectando Modelo do Dispositivo...')
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
        return {"Erro": "Dispositivo desconhecido"}
    
    # Fix files
    try:
        fixed_file = process_file_fixer(whats_main_folder_file, dispositivo)
        print(f'Arquivo corrigido: {fixed_file}')
    except Exception as e:
        return {"Erro": f"Erro ao processar arquivo: {str(e)}"}
    
    attached_files: Tuple[Optional[str], ...] = tuple(obj['name'] for obj in file_obj_list if obj.get('name'))
        
    # Extract info based on device type
    print(f'{dispositivo.title()} detectado!')
    print('Processando Arquivos e Mídia...')
    
    try:
        extracted_info = extract[dispositivo](fixed_file)
    except Exception as e:
        return {"Erro": f"Erro ao extrair informações: {str(e)}"}
    
    # Append files
    try:
        list_files = file_appending(extracted_info, transcriptions)
        list_files_pdf = file_appending_pdf(extracted_info, pdf_img_links)
    except Exception as e:
        return {"Erro": f"Erro ao processar anexos: {str(e)}"}

    print('Organizando Mensagens...')

    # Create JSON output
    output_path = os.path.join(final_work_folder, 'output.json')
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(list_files, f, ensure_ascii=False, indent=2)
        
        # Read the JSON file and return its contents
        with open(output_path, 'r', encoding='utf-8') as f:
            result: List[TMessageData] = json.load(f)
    except Exception as e:
        return {"Erro": f"Erro ao salvar ou ler o resultado: {str(e)}"}
    
    # Add ZIP analysis data to the result if available
    if zip_analysis_data:
        # Store analysis results in a separate file
        analysis_path = os.path.join(final_work_folder, 'analysis.json')
        try:
            with open(analysis_path, 'w', encoding='utf-8') as f:
                json.dump(zip_analysis_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Aviso: Não foi possível salvar dados de análise: {str(e)}")
    
    print('Processamento Finalizado!')
    return {"sucesso": True, "resultado": result, "analise": zip_analysis_data}


def main():
    """Função principal para executar o processamento offline"""
    
    # Caminho do arquivo conforme especificado
    file_path = "/home/brpl/code/whats-organizer-testing/iphone/teste-conversa-simples-sem-nada-bruno-iphone-comeca.zip"
    
    # Gerar um nome único para a pasta de trabalho
    unique_folder_name = f"processing_{uuid.uuid4().hex[:8]}"
    
    print(f"Iniciando processamento do arquivo: {file_path}")
    print(f"Pasta de trabalho: {unique_folder_name}")
    print("-" * 50)
    
    try:
        resultado = process_convo(file_path, unique_folder_name)
        
        if "Erro" in resultado:
            print(f"❌ ERRO: {resultado['Erro']}")
        else:
            print("✅ Processamento concluído com sucesso!")
            print(f"📊 Mensagens processadas: {len(resultado.get('resultado', []))}")
            if resultado.get('analise', {}).get('detected_device'):
                print(f"📱 Dispositivo detectado: {resultado['analise']['detected_device']}")
            if resultado.get('analise', {}).get('whatsapp_contact'):
                print(f"👤 Contato: {resultado['analise']['whatsapp_contact']}")
                
    except Exception as e:
        print(f"❌ ERRO INESPERADO: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()