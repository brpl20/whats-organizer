import os
import asyncio
from os.path import abspath
import subprocess
from subprocess import STDOUT, PIPE
from typing import List, TypedDict, TypeAlias, cast
from dotenv import load_dotenv
import aiohttp
import json
from sanitize import sanitize_path

load_dotenv(override=True)
api_key = os.getenv("OPENAI_API_KEY")

class Transcription(TypedDict):
    FileName: str
    Transcription: str

TranscriptionList: TypeAlias = List[Transcription]

async def transcribe_file(session, mp3_file_path, file_name):
    """Transcribe a single file using OpenAI Whisper API"""
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    with open(mp3_file_path, 'rb') as f:
        form_data = aiohttp.FormData()
        form_data.add_field('file', f.read(), filename=os.path.basename(mp3_file_path))
        form_data.add_field('model', 'whisper-1')
        
        async with session.post(url, headers=headers, data=form_data) as response:
            result = await response.json()
            transcript = result.get('text', '')
            print(f"Transcrição de {file_name}...")
            print(transcript)
            return {'FileName': file_name, 'Transcription': transcript}

async def convert_opus_to_mp3_async(path: str) -> TranscriptionList:
    """Convert opus files to mp3 and transcribe them concurrently"""
    transcriptions_list: TranscriptionList = []

    if not os.path.isdir(path):
        print(f"The specified path {path} does not exist or is not a directory.")
        return transcriptions_list
    
    if not api_key:
        print("Não foi detectada uma chave OPENAI")
        return []

    # First convert all opus files to mp3
    conversion_tasks = []
    file_info = []
    
    for file_name in os.listdir(path):
        if file_name.endswith('.opus'):
            cwd = os.path.dirname(__file__)
            opus_file_path = abspath(os.path.join(cwd, path, file_name))
            mp3_file_path = abspath(opus_file_path.replace('.opus', '.mp3'))
            opus_file_path = sanitize_path(opus_file_path)
            mp3_file_path = sanitize_path(mp3_file_path)
            
            command = ['ffmpeg', '-i', opus_file_path, '-acodec', 'libmp3lame', mp3_file_path]
            process = subprocess.Popen(command, stdout=PIPE, stderr=STDOUT, text=True)
            conversion_tasks.append(process)
            file_info.append((file_name, mp3_file_path))
    
    # Wait for all conversions to complete
    for process in conversion_tasks:
        stdout, stderr = process.communicate()
        if int(process.returncode or 0):
            print(f"[{process.returncode}] Failed to convert a file.\n\n{stdout}\n\n{stderr}")
            return transcriptions_list
    
    # Now transcribe all mp3 files concurrently
    async with aiohttp.ClientSession() as session:
        transcription_tasks = []
        for file_name, mp3_file_path in file_info:
            task = transcribe_file(session, mp3_file_path, file_name)
            transcription_tasks.append(task)
        
        transcriptions = await asyncio.gather(*transcription_tasks)
        transcriptions_list.extend(transcriptions)
    
    return transcriptions_list

def convert_opus_to_mp3(path: str) -> TranscriptionList:
    """Synchronous wrapper for the async function"""
    return asyncio.run(convert_opus_to_mp3_async(path))
