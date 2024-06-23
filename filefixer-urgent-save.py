import re
# Process to remove invalid characters
# Process to join lines that don't start with date time format

# def line_to_join(line, number):
#     processed_lines = []
#     line_befor = line[-number]


def process_chat_files(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
        #print(lines)
        # Initialize the processed lines container
        processed_lines = []
        processed_lines_clean = []
        processed_lines_final = []

        # Regular expression for lines starting with date time format
        pattern = r'^\[\d{2}\/'
        pattern_iphone = r'^\d{2}\/'
        #print(pattern)
        # Clean the invalid characters
        # prin(line)

    for index, line in enumerate(lines):
        cleaned_line = line.strip()
        processed_lines.append(cleaned_line)
    
    for index, line in enumerate(processed_lines):
        line = line.replace('\u200e', '')
        #print(index)
        #print(line)
        if line and not cleaned_line.isspace():
            processed_lines_clean.append(line)

    for line in processed_lines_clean:
        match = re.match(pattern_iphone, line)
        if match:
            processed_lines_final.append(line.strip())  # Append the matched line or its processed version

        elif not re.match(pattern_iphone, line):
            joiner = processed_lines_final[-1] + line
            processed_lines_final.pop()
            processed_lines_final.append(joiner)
        else:
            print("Error")

    for line in processed_lines_final:
        print(line)

    with open('./paulochat_fixed.txt', 'w') as file:
        for line in processed_lines_final:
            file.write(line + '\n')  # Add a newline character after each line


process_chat_files('./paulochat.txt')
