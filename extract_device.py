from os import PathLike
import re
from typing import Literal, TypeAlias, Union

Mobile: TypeAlias = Literal['andoid', 'iphone']

def extract_info_device(input_file: Union[str, bytes, PathLike]) -> Mobile:
    
    # iphone
    message_pattern_iphone = r'\] (.*?): (.*)'
    
    # android
    message_pattern_android = r'\d{2}/\d{2}/\d{2,4} \d{2}:\d{2} - '


    with open(input_file, 'r', encoding='utf-8', errors='ignore') as file:
        lines = file.readlines(50)

    for line in lines:
        matches_iphone = re.search(message_pattern_iphone, line)
        matches_android = re.search(message_pattern_android, line)
        
        message_device = ''
        
        if matches_android:
            message_device = "android"
        elif matches_iphone:
            message_device = "iphone"
        else:
            print("Erro: Dispositivo ou formato do texto não detectado")
        return message_device or "android"
    
    
