import re
from typing import List
from extract_device import Mobile

def process_file_fixer(filename: str, device: Mobile) -> str:
    with open(filename, 'r', errors="ignore") as file:
        lines = file.readlines()

    pattern = re.compile(r'^\d{2}\/' if device == 'android' else r'^\[\d{2}\/')
    regex_remove_text_order = re.compile(r'[\u200e\u200f]')

    newfile = filename + "_fixed.txt"
    with open(newfile, 'w') as file:
        previous_line = ''
        for line in lines:
            line = regex_remove_text_order.sub('', line).strip()
            if not line:
                continue

            if pattern.match(line):
                if previous_line:
                    file.write(previous_line + '\n')
                previous_line = line
            else:
                previous_line += line

        if previous_line:
            file.write(previous_line + '\n')

    return newfile