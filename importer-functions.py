import re
import json
import codecs
from bs4 import BeautifulSoup
from filefixer import process_chat_files
import fitz


def decode_unicode_escape(string_with_escapes):
    decoded_string = codecs.decode(string_with_escapes, 'unicode-escape')
    return decoded_string

def parse_chat_messages(text):
    message_pattern = re.compile(r'\[(\d{2}/\d{2}/\d{4}), (\d{2}:\d{2}:\d{2})\] (.*?):\s(.*)')

    messages = []
    unique_senders = {}
    for line_number, line in enumerate(text.split("\n")):
        attachment = None
        match = message_pattern.match(line)
        if match:
            date, time, sender, message = match.groups()
            if sender not in unique_senders:
                unique_senders[sender] = len(unique_senders) + 1
                sender_id = unique_senders[sender]

            messages.append({
                "id": len(messages) + 1,
                "date": date,
                "time": time,
                "sender": sender,
                "sender_id": sender_id,
                "message": message,
                "attachment": attachment
            })
    return messages

def parse_chat_messages_attachments(dicttowork):
    attachment_pattern = re.compile(r'<anexado:\s([^<>]+)>')
    messages = dicttowork
    for dict in dicttowork:
        mensagem = dict.get('message')
        attachment_match = attachment_pattern.match(mensagem)
        if attachment_match:
            dict['attachment'] = attachment_match.group(1)
    return messages

with open('./whats/_chat2.txt', mode='r', encoding='UTF-8') as file:
    text = decode_unicode_escape(file.read())



objectToWork = parse_chat_messages(text)
parsed = parse_chat_messages_attachments(objectToWork)


html = ""

for message in parsed:
    if message['attachment'] is not None and message['attachment'].endswith('.opus'):
        print(message['attachment'])
    if message['attachment'] is not None and message['attachment'].endswith('.pdf'):
        print(message['attachment'])
    if message['attachment'] is not None and message['attachment'].endswith('.jpg'):
        print(message['attachment'])
    if message['attachment'] is not None and message['attachment'].endswith('.vcf'):
        print(message['attachment'])
    




#print(html)

#print(parse_chat_messages(text))
#print(parse_chat_messages(text)[300][1])
# json_data = json.dumps(parse_chat_messages(text), indent=4, ensure_ascii=False)

