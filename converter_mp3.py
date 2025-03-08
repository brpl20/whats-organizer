import os
from os.path import abspath
import subprocess
from subprocess import STDOUT, PIPE
from typing import List, TypedDict, TypeAlias, cast
from dotenv import load_dotenv 
from re import sub

from sanitize import sanitize_path


load_dotenv(override=True)
api_key = os.getenv("OPENAI_API_KEY")
# clientopenai = OpenAI(api_key='')

class Transcription(TypedDict):
    FileName: str
    Transcription: str

TranscriptionList: TypeAlias = List[Transcription]

def convert_opus_to_mp3(path: str) -> TranscriptionList:


    transcriptions_list: TranscriptionList = []

    if not os.path.isdir(path):
        print(f"The specified path {path} does not exist or is not a directory.")
        return transcriptions_list
    
    if api_key:
        # Import here so it works without a key hopefully :^)
        from openai import OpenAI
        client = OpenAI(api_key=api_key) if api_key else None 

    for file_name in os.listdir(path):
        if file_name.endswith('.opus'):
            cwd = os.path.dirname(__file__)
            opus_file_path = abspath(os.path.join(cwd, path, file_name))
            mp3_file_path = abspath(opus_file_path.replace('.opus', '.mp3'))
            opus_file_path = sanitize_path(opus_file_path)
            mp3_file_path = sanitize_path(mp3_file_path)
            command = ['ffmpeg', '-i', opus_file_path, '-acodec', 'libmp3lame', mp3_file_path]
            process = subprocess.Popen(command, stdout=PIPE, stderr=STDOUT, text=True)
            stdout, stderr = process.communicate()

            if int(process.returncode or 0):
                print(f"[{process.returncode}] Failed to convert {file_name}.\n\n{' '.join(command)}\n\n{stdout}\n\n{stderr}")
                return transcriptions_list
                
            # WhisperTranscribe
            if (not client):
                print("Não foi detectada uma chave OPENAI")
                return []
            with open(mp3_file_path, 'rb') as f:
                files = {'file': f}
                transcript = client.audio.transcriptions.create(model="whisper-1",file=f)
                transcriptions_list.append({'FileName': file_name, 'Transcription': transcript.text})
                print("Transcrição...")
                print(transcript.text)
    #pdb.set_trace()
    return transcriptions_list
