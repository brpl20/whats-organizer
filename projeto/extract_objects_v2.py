import re
import os


def extract_info_iphone(input_file):
    extracted_info = []
    unique_names = set()
    unique_ids = {}
    date_time_pattern = r'\[(\d{2}/\d{2}/\d{4}), (\d{2}:\d{2}:\d{2})\]'
    message_pattern = r'\] (.*?): (.*)'

    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for line in lines:
        matches = re.findall(message_pattern, line)

        if matches:
            name = matches[0][0]
            unique_names.add(name)
            #print(len(unique_names))

        date_time_match = re.search(date_time_pattern, line)
        if date_time_match:
            date = date_time_match.group(1)
            time = date_time_match.group(2)

        message_match = re.search(message_pattern, line)
 
        if message_match:
            sender = message_match.group(1)
            message = message_match.group(2)
            file_attached = False

            if sender not in unique_ids:
                unique_ids[sender] = len(unique_ids) + 1
            sender_id = unique_ids[sender]

            if any(ext in message for ext in ['.docx', '.jpg']):
                file_pattern = r'(\S+)\.(docx|jpg)'
                file_match = re.search(file_pattern, message)
                if file_match:
                    file_attached = file_match.group()

            elif any(ext in message for ext in ['.opus']):
                file_pattern = r'(\S+)\.(opus)'
                file_match = re.search(file_pattern, message)
                file_attached = file_match.group()

            elif '.pdf' in message:
                file_pattern_pdf = r'<anexado:\s*(.*?\.pdf)>'
                file_pattern_pdf_match = re.search(file_pattern_pdf, message)
                #print(file_pattern_pdf_match)
                if file_pattern_pdf_match:
                    file_attached = file_pattern_pdf_match.group(0)

            extracted_info.append({'Name': sender, 'ID': sender_id, 'Date': date, 'Time': time, 'Message': message, 'FileAttached': file_attached})
    
    if len(unique_names) > 2:
        # Limpa a lista de entradas anteriores
        extracted_info.clear()
        # Adiciona a nova entrada no início da lista
        extracted_info.insert(0, {'ERRO': "Conversas em grupo não suportadas"})
        # Levanta um erro
        #raise ValueError("Conversas em grupo não suportadas")
        # print(extract_info)
        return extracted_info
    else:
        extracted_info.append({'Name': sender, 'ID': sender_id, 'Date': date, 'Time': time, 'Message': message, 'FileAttached': file_attached})
        return extracted_info

def extract_info_android(input_file):
    extracted_info = []
    unique_names = set()
    unique_ids = {}
    date_time_pattern = r'(\d{2}/\d{2}/\d{4}) (\d{2}:\d{2}) -'
    message_pattern = r'- (.*?): (.*)'

    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for line in lines:
        matches = re.findall(message_pattern, line)

        if matches:
            name = matches[0][0]
            unique_names.add(name)
            #print(len(unique_names))

        date_time_match = re.search(date_time_pattern, line)
        if date_time_match:
            date = date_time_match.group(1)
            time = date_time_match.group(2)

        message_match = re.search(message_pattern, line)
 
        if message_match:
            sender = message_match.group(1)
            message = message_match.group(2)
            file_attached = False

            if sender not in unique_ids:
                unique_ids[sender] = len(unique_ids) + 1
            sender_id = unique_ids[sender]

            if any(ext in message for ext in ['.docx', '.jpg']):
                file_pattern = r'(\S+)\.(docx|jpg)'
                file_match = re.search(file_pattern, message)
                if file_match:
                    file_attached = file_match.group()

            elif any(ext in message for ext in ['.opus']):
                file_pattern = r'(\S+)\.(opus)'
                file_match = re.search(file_pattern, message)
                file_attached = file_match.group()

            elif '.pdf' in message:
                file_pattern_pdf = r'<anexado:\s*(.*?\.pdf)>'
                file_pattern_pdf_match = re.search(file_pattern_pdf, message)
                #print(file_pattern_pdf_match)
                if file_pattern_pdf_match:
                    file_attached = file_pattern_pdf_match.group(0)

            extracted_info.append({'Name': sender, 'ID': sender_id, 'Date': date, 'Time': time, 'Message': message, 'FileAttached': file_attached})
    
    if len(unique_names) > 2:
        # Limpa a lista de entradas anteriores
        extracted_info.clear()
        # Adiciona a nova entrada no início da lista
        extracted_info.insert(0, {'ERRO': "Conversas em grupo não suportadas"})
        # Levanta um erro
        #raise ValueError("Conversas em grupo não suportadas")
        # print(extracted_info)
        return extracted_info
    else:
        extracted_info.append({'Name': sender, 'ID': sender_id, 'Date': date, 'Time': time, 'Message': message, 'FileAttached': file_attached})
        return extracted_info