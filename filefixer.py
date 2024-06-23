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

    for index, line in enumerate(processed_lines_clean):
        print(line)


    return(processed_lines_clean)

process_chat_files('./paulochat.txt')
#print(process_chat_files('./paulochat.txt'))



    for index, line in enumerate(lines):
        cleaned_line = line.strip()
        #print(cleaned_line)
        # If the line doesn't start with date time format, join with last line
        match = re.match(pattern_iphone, cleaned_line)
        
        if match:
            processed_lines.append(cleaned_line)
            cleaned_line_number = index
            #print(cleaned_line)
        elif not re.match(pattern_iphone, cleaned_line):
            if cleaned_line and not cleaned_line.isspace():
                joiner = processed_lines[-1] + line
                processed_lines.pop()
                processed_lines.append(joiner)
                #print(line)
                #print(joiner)
                #processed_lines.pop()
                #print(processed_lines[-1])
                #print(processed_lines[-1])
        else:
            print("Error")


#     #print(processed_lines)

#      # Write to a new file 
#     with open('./paulochat_fixed.txt', 'w') as file:
#         for line in processed_lines:
#             #print(line)
#             file.write(line)


# process_chat_files('./paulochat.txt')
