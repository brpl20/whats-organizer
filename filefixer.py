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
        pattern = r'^\[\d{2}\/'

    # for line in lines:
        # Clean the invalid characters
        # prin(line)
        # processed_lines.append(line)
        # line = line.replace('\u200e', '')


    for line in lines:
        cleaned_line = line.strip()
        # If the line doesn't start with date time format, join with last line
        if not re.match(pattern, cleaned_line):
            joiner = line[-1] + line
            print(joiner)
            processed_lines.append(joiner)
        else:
            processed_lines.append(line)


        
     # Write to a new file 
    with open('./whats/_chat_to_join_fixed.txt', 'w') as file:
        for line in processed_lines:
            file.write(line)


process_chat_files('./whats/_chat_to_join.txt')