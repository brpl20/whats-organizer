import re
import os

# Regular expression pattern
pattern = r'^\[\d\d/\d\d/\d{4}, \d\d:\d\d:\d\d\].*'

# Input and output file paths
input_file = './whats/_chat_to_join.txt'
output_file = 'output.txt'

match_count = 0
output_string = ""

if os.path.exists(output_file):
    os.remove(output_file)

with open('./whats/_chat_to_join.txt', 'a') as file:
    file.write('[00/00/0000, 00:00:00]\n')    # add last line needed to process the next to last line

with open(input_file, 'r') as file:
    for line in file:
        line = line.rstrip("\n")
        if match_count > 0 and re.search(pattern, line):
            match_count = 0
            # match with match_count > 0, output line and set match_count to 0
            with open(output_file, 'a') as output:
                if output_string != "[00/00/0000, 00:00:00]":
                    output.write(output_string + "\n")
                    output_string = line
        # Check if line matches the pattern and the match_count is 0
        if match_count == 0 and re.search(pattern, line):
            match_count += 1
            # match found, save line to output string
            output_string = line

        if match_count > 0 and not re.search(pattern, line):
            # append line to output string
            output_string = output_string + " || " + line
