import re
# Process to remove invalid characters
# Process to join lines that don't start with date time format
def process_chat_files(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
        #print(lines)
        # Initialize the processed lines container
        processed_lines = []
        # Regular expression for lines starting with date time format
        pattern = r'^\[\d{2}/\d{2}/\d{4}, \d{2}:\d{2p}:\d{2}\]'
        last_line = ''

    for line in lines:
        # Clean the invalid characters
        line = line.replace('\u200e', '')
        # If the line doesn't start with date time format, join with last line
        if not re.match(pattern, line):
            if last_line != '':
                processed_lines[-1] = f'{last_line.strip()} {line}'
                continue
                
        # If the line starts with the date time format, add to the processed lines 
        processed_lines.append(line)
        last_line = line


        
     # Write to a new file 
    with open('chat2-----fixed.txt', 'w') as file:
        for line in processed_lines:
            file.write(line)

    return 'fixed_file2.txt'

process_chat_files('_chat.txt')