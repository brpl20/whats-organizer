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
from file_append import file_appending


print("Criando pasta de trabalho única")
base_folder = "./zip_tests/"
unique_folder_name = str(uuid.uuid4())
final_work_folder = base_folder + unique_folder_name

print("Extraindo Arquivos .zip") 
handle_zip_file("./zip_tests/rose.zip", final_work_folder)

print("Listando Objetos do Diretório") 
file_object = list_files_in_directory(final_work_folder)

print("Converter MP3 e transcrever...")
transcriptions = convert_opus_to_mp3(final_work_folder)

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
    #pdb.set_trace()
elif dispositivo == "iphone":
    iphone = extract_info_iphone(fixed_file)
    list_files = file_appending(iphone, transcriptions)
    #pdb.set_trace()
else:
    print("Erro: Dispositivo não selecionado ou identificado")

print("Criando Arquivo Json")
with open('output.json', 'w') as f:
    json.dump(list_files, f)
