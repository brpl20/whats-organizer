import re
import os

def extract_info_by_device(input_file, device): 
    if device == "android":
        extract_info_android(input_file)
    elif device == "iphone":
        extract_info_iphone(input_file)
    else:
        print("Erro: Dispositivo não selecionado ou identificado")


def extract_info_android(input_file):
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

        message_match = re.search(message_pattern, line)
        if message_match:
            sender = message_match.group(1)
            message = message_match.group(2)

            file_attached = False

            if any(ext in message for ext in ['.docx', '.jpg']):
                file_pattern = r'(\S+)\.(pdf|jpg)'
                file_match = re.search(file_pattern, message)
                file_attached = file_match.group(0)

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
    #date_time_pattern = r'(\d{2}/\d{2}/\d{4} \d{2}:\d{2})' 
    date_time_pattern = r'(\d{2}/\d{2}/\d{4}) (\d{2}:\d{2}) -'
    #message_pattern = r'\] (.*?): (.*)'
    message_pattern = r'- (.*?): (.*)'



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
            #print(date)
            #print(time)


        message_match = re.search(message_pattern, line)
        if message_match:
            sender = message_match.group(1)
            message = message_match.group(2)

            file_attached = False

            ## PAREI AQUI 
            ## RESOLVER u200 antes 
            ## ROSOLVER UNIFICACAO DO TEXTO ANTES TAMBÉM
            if any(ext in message for ext in ['.docx', '.jpg']):
                file_pattern = r'(\S+)\.(pdf|jpg)'
                file_match = re.search(file_pattern, message)
                print(file_match.groups())
                file_attached = file_match.group(0)

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


extract_info_by_device('/Users/brpl20/code/whats-organizer/projeto/zip_tests/extracted/paulochat.txt', 'iphone')
extract_info_by_device('/Users/brpl20/code/whats-organizer/projeto/zip_tests/extracted/_chat.txt', 'android')

