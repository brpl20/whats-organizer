from dataclasses import dataclass
import re
from typing import List, Literal, Mapping, Optional, Set, TypeVar, TypedDict, Union
from os import PathLike

@dataclass(unsafe_hash=True)
class MessageData(TypedDict):
    Name: str
    ID: int
    Date: str
    Time: str
    Message: str
    FileAttached: Optional[Union[Literal[False], str]]
    
TMessageData = TypeVar("TMessageData", bound=Union[MessageData, Mapping[Literal["ERRO"], str]])

def extract_info_iphone(input_file: Union[str, bytes, PathLike]):
    extracted_info: List[TMessageData] = []
    unique_names: Set[str] = set()
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

            if any(ext in message for ext in ['.jpg']):
                file_pattern = r'(\S+)\.(jpg)'
                file_match = re.search(file_pattern, message)
                if file_match:
                    file_attached = file_match.group()

            # if any(ext in message for ext in ['.docx', '.jpg']):
            #     file_pattern = r'(\S+)\.(docx|jpg)'
            #     file_match = re.search(file_pattern, message)
            #     if file_match:
            #         if file_match.group(2) == 'docx':
            #             file_attached = file_match.group(1) + '.pdf'  # Only filename for DOCX
            #         else:
            #             file_attached = file_match.group()  # Full filename with extension for others
            if '.docx' in message:
                file_pattern = r'<anexado:\s*(.+?)\.docx>'
                file_match = re.search(file_pattern, message)
                if file_match:
                    file_attached = file_match.group(1) + '.pdf'  # Full filename with .pdf extension
                else:
                    file_attached = None  # or handle the case when no match is found

            elif any(ext in message for ext in ['.opus']):
                file_pattern = r'(\S+)\.(opus)'
                file_match = re.search(file_pattern, message)
                file_attached = file_match.group()

            elif any(ext in message for ext in ['.mp4']):
                file_pattern = r'(\S+)\.(mp4)'
                file_match = re.search(file_pattern, message)
                file_attached = file_match.group()

            elif '.pdf' in message:
                file_pattern_pdf = r'<anexado:\s*(.*?\.pdf)>'
                # file_pattern_pdf = r'<anexado:\s*(.*?\.pdf)>'
                file_pattern_pdf_match = re.search(file_pattern_pdf, message)
                #print(file_pattern_pdf_match)
                if file_pattern_pdf_match:
                    print("result")
                    print("-----------------------------")
                    file_attached = file_pattern_pdf_match.group(1)
                    print(file_attached)

            extracted_info.append(
                MessageData(**{
                    'Name': sender,
                    'ID': sender_id,
                    'Date': date,
                    'Time': time,
                    'Message': message,
                    'FileAttached': file_attached
                })
            )
    
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
        extracted_info.append(
            MessageData(**{
                'Name': sender,
                'ID': sender_id,
                'Date': date,
                'Time': time,
                'Message': message,
                'FileAttached': file_attached
            })
        )
        return extracted_info


def extract_info_android(input_file: Union[str, bytes, PathLike]):
    extracted_info: List[TMessageData] = []
    unique_names: Set[str] = set()
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

            if any(ext in message for ext in ['.jpg']):
                file_pattern = r'(\S+)\.(jpg)'
                file_match = re.search(file_pattern, message)
                if file_match:
                    file_attached = file_match.group()

            # if any(ext in message for ext in ['.docx', '.jpg']):
            #     file_pattern = r'(\S+)\.(docx|jpg)'
            #     file_match = re.search(file_pattern, message)
            #     if file_match:
            #         if file_match.group(2) == 'docx':
            #             file_attached = file_match.group(1) + '.pdf'  # Only filename for DOCX
            #         else:
            #             file_attached = file_match.group()  # Full filename with extension for others

            
            if any(ext in message for ext in ['.docx']):
                # print("message")
                # print(message)
                # #file_pattern = r'(\S+)\.(docx)'
                # file_pattern = r'(.*?\.docx)'
                # file_match = re.search(file_pattern, message)
                # print("FILE MATCH =>")
                # print(file_match)
                # if file_match:
                #     file_attached = file_match.group(1) + '.pdf'  # Full filename with .pdf extension
                #     print("FINAL FILE")
                #     print("--------------")
                #     print(file_attached)
                #     file_attached2 = file_match.group(0)
                #     print("FINAL FILE")
                #     print("--------------")
                #     print(file_attached2)
                # Updated regex pattern to capture the filename without extension
                file_pattern = r'(.*?)\.docx'
                file_match = re.search(file_pattern, message)
                
                print("FILE MATCH =>")
                print(file_match)
                
                if file_match:
                    # Extract the filename without extension and add .pdf
                    file_attached = file_match.group(1) + '.pdf'
                    print("FINAL FILE")
                    print("--------------")
                    print(file_attached)                
                else:
                    file_attached = None  # or handle the case when no match is found

            elif any(ext in message for ext in ['.opus']):
                file_pattern = r'(\S+)\.(opus)'
                file_match = re.search(file_pattern, message)
                file_attached = file_match.group()

            elif any(ext in message for ext in ['.mp4']):
                file_pattern = r'(\S+)\.(mp4)'
                file_match = re.search(file_pattern, message)
                file_attached = file_match.group()

            elif any(ext in message for ext in ['.pdf']):
                # file_pattern_pdf = r'(\S+)\.(pdf)'
                file_pattern_pdf = r'([\d\w]+\.pdf)'
                # file_pattern_pdf = r'<anexado:\s*(.*?\.pdf)>'
                #file_pattern_pdf = r'<anexado:\s*(.*?\.pdf)>'
                #file_pattern_pdf = r'<anexado:\s*(.*?\.pdf)>'

                file_pattern_pdf_match = re.search(file_pattern_pdf, message)
                #print(file_pattern_pdf_match)
                if file_pattern_pdf_match:
                    file_attached = file_pattern_pdf_match.group(1)
                    print("result")
                    print("-----------------------------")
                    print(file_attached)

            extracted_info.append(
                MessageData(**{
                    'Name': sender,
                    'ID': sender_id,
                    'Date': date,
                    'Time': time,
                    'Message': message,
                    'FileAttached': file_attached
                })
            )
    
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
        extracted_info.append(
            MessageData(**{
                'Name': sender,
                'ID': sender_id,
                'Date': date,
                'Time': time,
                'Message': message,
                'FileAttached': file_attached
            })
        )
        return extracted_info



    # if len(unique_names) > 2:
    #     # Limpa a lista de entradas anteriores
    #     extracted_info.clear()
    #     # Adiciona a nova entrada no início da lista
    #     extracted_info.insert(0, {'ERRO': "Conversas em grupo não suportadas"})
    #     # Levanta um erro
    #     #raise ValueError("Conversas em grupo não suportadas")
    #     # print(extracted_info)
    #     return extracted_info
    # else:
    #     extracted_info.append({'Name': sender, 'ID': sender_id, 'Date': date, 'Time': time, 'Message': message, 'FileAttached': file_attached})
    #     return extracted_info