import os
from os.path import abspath
import subprocess
from subprocess import STDOUT, PIPE
from dotenv import load_dotenv 
from openai import OpenAI
from re import sub

from sanitize import sanitize_path


load_dotenv()
api_key = os.getenv("WHISPER")
clientopenai = OpenAI(api_key=api_key)
# clientopenai = OpenAI(api_key='')
transcriptions_list = []

def add_transcription(file_name, transcription):
    transcriptions_list.append({'FileName': file_name, 'Transcription': transcription})


def convert_opus_to_mp3(path, client=clientopenai):
    if not os.path.isdir(path):
        print(f"The specified path {path} does not exist or is not a directory.")
        return
    for file_name in os.listdir(path):
        if file_name.endswith('.opus'):
            cwd = os.path.dirname(__file__)
            opus_file_path = abspath(os.path.join(cwd, path, file_name))
            mp3_file_path = abspath(opus_file_path.replace('.opus', '.mp3'))
            opus_file_path = sanitize_path(opus_file_path)
            mp3_file_path = sanitize_path(mp3_file_path)
            command = ['ffmpeg', '-i', opus_file_path, '-acodec', 'libmp3lame', mp3_file_path]
            process = subprocess.Popen(command, stdout=PIPE, stderr=STDOUT, text=True)
            process.communicate()

            if int(process.returncode or 0):
                stdout, stderr = process.communicate()
                print(f"[{process.returncode}] Failed to convert {file_name}.\n\n{' '.join(command)}\n\n{stdout}\n\n{stderr}")
                return []
                
            # WhisperTranscribe
            with open(mp3_file_path, 'rb') as f:
                files = {'file': f}
                transcript = client.audio.transcriptions.create(model="whisper-1",file=f)
                add_transcription(file_name, transcript.text)
                print("Transcrição...")
                print(transcript.text)
    #pdb.set_trace()
    return transcriptions_list
