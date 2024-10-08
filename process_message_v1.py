import re
import csv
import os
import uuid
import pdb
import json

from openai import OpenAI
from pydub import AudioSegment

from handle_zip_file import handle_zip_file
from list_files import list_files_in_directory
from find_whats_key_data import find_whats_key
from extract_device import extract_info_device
from file_fixer import process_file_fixer 
from extract_objects_v2 import extract_info_iphone, extract_info_android
from converter_mp3 import convert_opus_to_mp3
from converter_pdf import process_pdf_folder
from file_append import file_appending, file_appending_pdf

def handle_zip(base_folder, max_size_mb, unique_folder): 
    final_work_folder = base_folder + unique_folder
    max_size_bytes = max_size_mb * 1024 * 1024
    file_size = os.path.getsize(base_folder)
    if file_size > max_size_bytes:
        return False, f'File is too large. Maximum size allowed is {max_size_mb} MB.'
    else: 
        handle_zip_file("./zip_tests/android2.zip", final_work_folder)
        return True, 'File handled successfully.', final_work_folder


print("Criando pasta de trabalho única")
base_folder1 = "./zip_tests/"
unique_folder1 = str(uuid.uuid4())
success, message, final_work_folder = handle_zip(base_folder1, 100, unique_folder1)

print("Listando Objetos do Diretório") 
file_object = list_files_in_directory(final_work_folder)

print("Converter MP3 e transcrever...")
transcriptions = convert_opus_to_mp3(final_work_folder)

print("Converter PDF, transformar em imagens e links")
bucket_name = 'tempfilesprocessing'
pdf_img_links = process_pdf_folder(final_work_folder, bucket_name)

print("Extraíndo Conversa Principal")
whats_main_file = find_whats_key(file_object)
whats_main_folder_file = final_work_folder + "/" + whats_main_file

print("Extraindo Dispositivo")
dispositivo = extract_info_device(whats_main_folder_file)
print(dispositivo)

print("Corrigindo Arquivos")
fixed_file = process_file_fixer(whats_main_folder_file, dispositivo)

print("extracting info") 
if dispositivo == "android":
    android = extract_info_android(fixed_file)
    list_files = file_appending(android, transcriptions)
    lit_files_pdf = file_appending_pdf(android, pdf_img_links)
    #pdb.set_trace()
elif dispositivo == "iphone":
    iphone = extract_info_iphone(fixed_file)
    list_files = file_appending(iphone, transcriptions)
    lit_files_pdf = file_appending_pdf(iphone, pdf_img_links)
    #pdb.set_trace()
else:
    print("Erro: Dispositivo não selecionado ou identificado")

print("Criando Arquivo Json")
with open('output.json', 'w') as f:
    json.dump(list_files, f)
