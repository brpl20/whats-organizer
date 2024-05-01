import re

def process_text_file(input_file):
    # Regular expression pattern for the expected line pattern
    pattern = r'\[\d{2}/\d{2}/\d{4}, \d{2}:\d{2}:\d{2}\]'

    # Open input file for reading
    with open(input_file, 'r') as file:
        lines = file.readlines()

    # Process the lines
    processed_lines = []

    for index, line in enumerate(lines):
        if re.match(pattern, line):
            processed_lines.append(line)
        else:
            concatenated_line = lines[index-1] + line
            processed_lines.append(concatenated_line)

        # Output the processed lines
        #for line in processed_lines:
        #print(line)

    return(processed_lines)



# Usage example
input_file = "_chat_to_join.txt"

for line in process_text_file(input_file):
    print(line)