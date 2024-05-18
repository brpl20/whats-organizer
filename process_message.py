import re
import csv

def extract_info(input_file):
    extracted_info = []
    unique_names = set()
    date_time_pattern = r'\[(\d{2}/\d{2}/\d{4}), (\d{2}:\d{2}:\d{2})\]'
    message_pattern = r'\] (.*?): (.*)'

    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for line in lines:
        # names
        matches = re.findall(message_pattern, line)
        if matches:
            name = matches[0][0]
            unique_names.add(name)

        #  date and time
        date_time_match = re.search(date_time_pattern, line)
        if date_time_match:
            date = date_time_match.group(1)
            time = date_time_match.group(2)

        # message
        message_match = re.search(message_pattern, line)
        if message_match:
            sender = message_match.group(1)
            message = message_match.group(2)

            #attachments [ add more extension here]
            file_attached = False
            if any(ext in message for ext in ['.opus', '.pdf', '.jpg']):
                file_attached = True

            extracted_info.append({'Name': sender, 'Date': date, 'Time': time, 'Message': message, 'FileAttached': file_attached})


    with open('extracted_info.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Name', 'Date', 'Time', 'Message', 'FileAttached']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for item in extracted_info:
            writer.writerow(item)

    print("Extraction completed. Output saved to extracted_info.csv")


extract_info('input.txt')
