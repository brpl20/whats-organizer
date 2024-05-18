import re
import csv
import os
from openai import OpenAI
import whisper
from pydub import AudioSegment


# Initialize OpenAI client (WhisperKey)
client = OpenAI(api_key="")


#from docx import Document

def transcribe_audio(audio_file_path):
    with open(audio_file_path, 'rb') as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return transcription['text']


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
            if any(ext in message for ext in ['.docx', '.jpg']):
                file_pattern = r'(\S+)\.(pdf|jpg)'
                file_match = re.search(file_pattern, message)
                file_attached = file_match.group(0)
                print(file_attached)
            elif any(ext in message for ext in ['.opus']):
                # Convert opus to mp3
               # Example usage
                file_pattern = r'(\S+)\.(opus)'
                file_match = re.search(file_pattern, message)
                file_attached = file_match.group(0)
                #print(file_attached)
                path = os.path.join(os.getcwd(), 'whats', file_attached)

                path_mp3 = path + '.mp3'
                #convert_opus_to_mp3(path, path_mp3)
                #print(path)
                #transcribe_audio(path_mp3)
                #model = whisper.load_model("base")
                #result = model.transcribe(path)
                #print(result["text"])
                #print("Opus")
            elif '.pdf' in message:
                file_pattern_pdf = r'<anexado:\s*(.*?\.pdf)>'
                file_pattern_pdf_match = re.search(file_pattern_pdf, message)
                file_attached_pdf = file_pattern_pdf_match.group(1)
                print(file_attached_pdf)
                



            extracted_info.append({'Name': sender, 'Date': date, 'Time': time, 'Message': message, 'FileAttached': file_attached})
    
    return extracted_info



#transcription = transcribe_audio('/Users/brpl20/code/whats-organizer/whats/00000011-AUDIO-2020-01-28-12-18-23.opus')
#print(transcription)

extracted_info = extract_info('/Users/brpl20/code/whats-organizer/whats/_chat2.txt')

# for line in extracted_info:
#     print(line)
