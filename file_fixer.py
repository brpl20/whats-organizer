import re
from typing import Literal, List
# Juntar as linhas em branco 
# Remover caracteres indesejados
def process_file_fixer(filename: str, device: Literal["android", "iphone"]) -> str:
    print(filename)
    with open(filename, 'r', errors="ignore") as file:
        lines = file.readlines()
        processed_lines: List[str] = []
        processed_lines_clean = []
        processed_lines_final = []
        if device == 'android': 
            pattern = r'^\d{2}\/'
        else: 
            pattern = r'^\[\d{2}\/'

    for line in lines:
        cleaned_line = line.strip()
        processed_lines.append(cleaned_line)
        
    # indicação de caso o texto se leia da esquerda pra direita (Árabe é oposto)
    unicode_left_to_right = '\u200e'
    unicode_right_to_left = '\u200f'
    regex_remove_text_order = re.compile(f'{unicode_left_to_right}|{unicode_right_to_left}')
    
    for line in processed_lines:
        line = re.sub(regex_remove_text_order, unicode_left_to_right, '')
        if line and not cleaned_line.isspace():
            processed_lines_clean.append(line)

    for line in processed_lines_clean:
        match = re.match(pattern, line)
        if match:
            processed_lines_final.append(line.strip())  # Append the matched line or its processed version

        elif not re.match(pattern, line):
            joiner = processed_lines_final[-1] + line
            processed_lines_final.pop()
            processed_lines_final.append(joiner)
        else:
            print("Error")

    #for line in processed_lines_final:
    #    print(line)
    newfile = filename + "_fixed.txt"
    with open(newfile, 'w') as file:
        for line in processed_lines_final:
            file.write(line + '\n')  # Add a newline character after each line
    return newfile

