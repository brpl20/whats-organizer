import re

def extract_info_device(input_file):
    
    # iphone
    message_pattern_iphone = r'\] (.*?): (.*)'
    
    # android
    message_pattern_android = r'\d{2}/\d{2}/\d{4} \d{2}:\d{2} - '


    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for line in lines:
        matches_iphone = re.search(message_pattern_iphone, line)
        matches_android = re.search(message_pattern_android, line)
        
        message_device = "Erro: Dispositivo ou formato do texto não detectado"
        
        if matches_android:
            message_device = "android"
        elif matches_iphone:
            message_device = "iphone"
        return message_device
    
    
