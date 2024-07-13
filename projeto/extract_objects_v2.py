import re
import os


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
                print(file_attached)

            elif '.pdf' in message:
                file_pattern_pdf = r'<anexado:\s*(.*?\.pdf)>'
                file_pattern_pdf_match = re.search(file_pattern_pdf, message)
                file_attached = file_pattern_pdf_match.group(1)

            extracted_info.append({'Name': sender, 'Date': date, 'Time': time, 'Message': message, 'FileAttached': file_attached})
        if len(unique_names) > 2:
            raise ValueError("ERRO: Conversas em Grupo não suportadas")
        else: 
            return extracted_info

    return extracted_info


def extract_info_iphone(input_file):
    extracted_info = []
    unique_names = set()
    date_time_pattern = r'(\d{2}/\d{2}/\d{4}) (\d{2}:\d{2}) -'
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

        message_match = re.search(message_pattern, line)
        if message_match:
            sender = message_match.group(1)
            message = message_match.group(2)
            file_attached = False

            if any(ext in message for ext in ['.docx', '.jpg']):
                file_pattern = r'(\S+)\.(docx|jpg)'
                file_match = re.search(file_pattern, message)
                if file_match:
                    file_attached = file_match.group()

            elif any(ext in message for ext in ['.opus']):
                file_pattern = r'(\S+)\.(opus)'
                file_match = re.search(file_pattern, message)
                file_attached = file_match.group()
                print(file_attached)

            elif '.pdf' in message:
                file_pattern_pdf = r'<anexado:\s*(.*?\.pdf)>'
                file_pattern_pdf_match = re.search(file_pattern_pdf, message)
                file_attached = file_pattern_pdf_match.group(1)

            extracted_info.append({'Name': sender, 'Date': date, 'Time': time, 'Message': message, 'FileAttached': file_attached})
    
    if len(unique_names) > 2:
        raise ValueError("ERRO: Conversas em Grupo não suportadas")
    else: 
        return extracted_info