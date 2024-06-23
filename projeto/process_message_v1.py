import re
import csv
import os
from openai import OpenAI
import whisper
from pydub import AudioSegment

from handle_zip_file import handle_zip_file
from list_files import list_files_in_directory
from extract_device import extract_device

# Descomprimindo arquivo de WhatsApp 
handle_zip_file("./zip_tests/paulo.zip", "./zip_tests/extracted")

# Listando os Arquivos e Transformando em um objeto 
# Testando se a conversa de WhatsApp é Encontrada 
# Selecionando a Conversa do Whats
file_object = list_files_in_directory("./zip_tests/extracted")

# Achando Conversa a ser trabalhada
def find_whats_key(data):
    for item in data:
        if 'whats' in item:
            return item['whats']
    return None

whats_main_file = find_whats_key(file_object)

# Extraindo Informação do Dispositivo 
# Através do Texto Inicial 
# extract_device(resultado do find_whats_key)


def extract_info(input_file):
    extracted_info = []
    unique_names = set()
    date_time_pattern = r'\[(\d{2}/\d{2}/\d{4}), (\d{2}:\d{2}:\d{2})\]'
    message_pattern = r'\] (.*?): (.*)'

    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for line in lines:
        matches = re.findall(message_pattern, line)

        if matches:
            name = matches[0][0]
            unique_names.add(name)

        date_time_match = re.search(date_time_pattern, line)
        if date_time_match:
            date = date_time_match.group(1)
            time = date_time_match.group(2)
            print(date)
            print(time)

        message_match = re.search(message_pattern, line)
        if message_match:
            sender = message_match.group(1)
            message = message_match.group(2)

            file_attached = False

            if any(ext in message for ext in ['.docx', '.jpg']):
                file_pattern = r'(\S+)\.(pdf|jpg)'
                file_match = re.search(file_pattern, message)
                file_attached = file_match.group(0)
                #print(file_attached)

            elif any(ext in message for ext in ['.opus']):
                file_pattern = r'(\S+)\.(opus)'
                file_match = re.search(file_pattern, message)
                file_attached = file_match.group(0)
                path = os.path.join(os.getcwd(), 'whats', file_attached)
                path_mp3 = path + '.mp3'
                #convert_opus_to_mp3(path, path_mp3)
                #print(path)
                #transcribe_audio(path_mp3)
                #model = whisper.load_model("base")
                #result = model.transcribe(path)
                #print(result["text"])
                #print("Opus")

            elif '.pdf' in message:
                file_pattern_pdf = r'<anexado:\s*(.*?\.pdf)>'
                file_pattern_pdf_match = re.search(file_pattern_pdf, message)
                file_attached_pdf = file_pattern_pdf_match.group(1)
                #print(file_attached_pdf)
                



            extracted_info.append({'Name': sender, 'Date': date, 'Time': time, 'Message': message, 'FileAttached': file_attached})
    
    return extracted_info



def extract_info_iphone(input_file):
    extracted_info = []
    unique_names = set()
    date_time_pattern = r'(\d{2}/\d{2}/\d{4} \d{2}:\d{2})' 
    message_pattern = r'- (.*?): (.*)'

    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for line in lines:
        date_time_match = re.search(date_time_pattern, line)
        if date_time_match:
            date_time = date_time_match.group(1)
            date, time = date_time.split()

        message_match = re.search(message_pattern, line)
        if message_match:
            sender = message_match.group(1)
            unique_names.add(sender)
            message = message_match.group(2)

            # Initialize file_attached as False for each message
            file_attached = False

            # ... (Rest of your code to detect and process file attachments)

            extracted_info.append({
                'Name': sender, 
                'Date': date, 
                'Time': time, 
                'Message': message, 
                'FileAttached': file_attached
    
            })
    
    return extracted_info

#extracted_info = extract_info('/Users/brpl20/code/whats-organizer/projeto/zip_tests/extracted/_chat.txt')
#print(extracted_info)

extracted_info2 = extract_info_iphone('/Users/brpl20/code/whats-organizer/projeto/zip_tests/extracted/paulochat.txt')
print(extracted_info2)
#print(extracted_info[12]["Name"])
#print(extracted_info[13]["Name"])
#print(extracted_info[14]["Name"])
#print(extracted_info[15]["Name"])

