import re
import os

def extract_info_device(input_file):
    # Android
    message_pattern_android = r'\] (.*?): (.*)'
    
    # iPhone
    message_pattern_iphone = r'\d{2}/\d{2}/\d{4} \d{2}:\d{2} - '


    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for line in lines:
        matches_android = re.search(message_pattern_android, line)
        matches_iphone = re.search(message_pattern_iphone, line)

        if matches_iphone:
            message_device = "iphone"
            return message_device
        elif matches_android:
            message_device = "android"
            return message_device
        else:
            message_device = "Erro: Dispositivo ou formato do texto não detectado"
            return message_device
    
    
