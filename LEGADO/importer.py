import re
import json
import codecs
import os
import zipfile

def decode_unicode_escape(string_with_escapes):
    decoded_string = codecs.decode(string_with_escapes, 'unicode-escape')
    return decoded_string

def open_file(file):
    with zipfile.ZipFile(file, 'r') as zip_ref:
        zip_ref.extractall()
        zip_path = os.path.join(os.getcwd(), file)
        return zip_path

def list_files():
    for file in os.listdir('.'):
        if file.endswith('.zip'):
            open_file(file)

def read_file(path)
    with open('./whats/_chat.txt', 'r') as file:
    text = file.read()
    #print(text)



 

# Date e Time
#pattern = re.compile(r'\[(\d{2}/\d{2}/\d{4}), (\d{2}:\d{2}:\d{2})\], (]\s(.*?):\s)')
pattern = re.compile(r'\[(\d{2}/\d{2}/\d{4}), (\d{2}:\d{2}:\d{2})\] (.*?):\s(.*)')
# Pattern to match text inside < >
attachment_pattern = r'<([^<>]+)>'
#pattern = re.compile(r'\[(\d{2}/\d{2}/\d{4}), (\d{2}:\d{2}:\d{2})\] (.*?):\s(.*?)<([^<>]+)>')



# List to store parsed messages
messages = []
sender1 = None
sender2 = None 
counter_lines = 0

# Parse each line of the text
for line in text.split("\n"):
    attachment_match = re.search(attachment_pattern, line)
    attachment_in_line = attachment_match.group() if attachment_match else None
    match = pattern.match(line)
    print(attachment_in_line)
    if counter_lines == 0:
        if match: 
            print(attachment_in_line)
            match = pattern.match(line)
            date = match.group(1)
            time = match.group(2)
            sender = match.group(3)
            message = match.group(4)
        # Create a dictionary for the message and append it to the list
            messages.append({
                "date": date,
                "time": time,
                "sender": sender,
                "sender_id": 1,
                "message": message,
                "attachment": attachment_in_line
            })
            counter_lines += 1
    else:
        if match:
            #attachment_match = re.search(attachment_pattern, line)
            print(attachment_in_line)
            print("iffff")
            date = match.group(1)
            time = match.group(2)
            sender = match.group(3)
            message = match.group(4)
            if sender == messages[0]['sender']:
                sender_id = 1
                # Create a dictionary for the message and append it to the list
                messages.append({
                    "date": date,
                    "time": time,
                    "sender": sender,
                    "sender_id": sender_id,
                    "message": message,
                    "attachment": attachment_in_line
                })
            else:
                if match:
                    #attachment_match = re.search(attachment_pattern, line)
                    print(attachment_in_line)
                    print("fffff")
                    sender_id = 2
                    date = match.group(1)
                    time = match.group(2)
                    sender = match.group(3)
                    message = match.group(4)
                    # Create a dictionary for the message and append it to the list
                    messages.append({
                        "date": date,
                        "time": time,
                        "sender": sender,
                        "sender_id": sender_id,
                        "message": message,
                        "attachment": attachment_in_line
                    })

# print(messages[0]['sender_id'], messages[0]['sender'], messages[0]['message'])
# print(messages[1]['sender_id'], messages[1]['sender'], messages[1]['message'])
# print(messages[2]['sender_id'], messages[2]['sender'], messages[2]['message'])
# print(messages[3]['sender_id'], messages[3]['sender'], messages[3]['message'])
# print(messages[4]['sender_id'], messages[4]['sender'], messages[4]['message'])
# print(messages[5]['sender_id'], messages[5]['sender'], messages[5]['message'])
# print(messages)

# Convert the list of dictionaries to JSON format
#json_data = json.dumps(messages, indent=4)
#print(decode_unicode_escape(json_data))

# Loop through the list of messages
for message in messages:
    # Check if the message contains an attachment pattern
    if "<anexado:" in message['message']:
        # Extract the attachment name and extension
        #print(message)
        attachment_pattern = r'<anexado: (.*?)>'
        attachment_match = re.search(attachment_pattern, message['message'])
        if attachment_match:
            attachment_name = attachment_match.group(1)
            # Process the attachment here
            # TODO: Implement your logic for handling attachments
            #print(f"Attachment found: {attachment_name}")


## PAREI AQUI 

# Convert the list of messages to JSON format
json_data = json.dumps(messages, indent=4)

# Create an HTML file
html_file = open("/Users/brpl20/code/whats-organizer/messages.html", "w")

# Write the HTML header
html_file.write("<html>\n<head>\n<style>\n")
html_file.write(".speaker1 { color: blue; }\n")
html_file.write(".speaker2 { color: green; }\n")
html_file.write("</style>\n</head>\n<body>\n")

# Loop through the messages and write them to the HTML file
for message in messages:
    # Determine the CSS class based on the speaker_id
    css_class = "speaker1" if message['sender_id'] == 1 else "speaker2"
    
    # Write the message to the HTML file with the appropriate CSS class
    html_file.write(f"<p class='{css_class}'>{message['date']} {message['time']}</p>")
    html_file.write(f"<p class='{css_class}'>{message['sender']}:</p>")
    
    # Escape the special characters in the message
    escaped_message = message['message'].replace("<", "&lt;").replace(">", "&gt;")
    
    html_file.write(f"<spam>{escaped_message}</spam>")

# Close the HTML file
html_file.close()