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
import concurrent.futures

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

def convert_single_file(opus_path, mp3_path):
    """Convert a single opus file to mp3"""
    command = ['ffmpeg', '-i', opus_path, '-acodec', 'libmp3lame', '-q:a', '2', mp3_path]
    process = subprocess.run(command, stdout=PIPE, stderr=STDOUT, text=True)
    return process.returncode == 0

async def process_file_async(session, file_name, path):
    """Process a single file: convert then transcribe"""
    cwd = os.path.dirname(__file__)
    opus_file_path = abspath(os.path.join(cwd, path, file_name))
    mp3_file_path = abspath(opus_file_path.replace('.opus', '.mp3'))
    opus_file_path = sanitize_path(opus_file_path)
    mp3_file_path = sanitize_path(mp3_file_path)
    
    # Use ProcessPoolExecutor for CPU-bound ffmpeg conversion
    with concurrent.futures.ProcessPoolExecutor() as pool:
        success = await asyncio.get_event_loop().run_in_executor(
            pool, convert_single_file, opus_file_path, mp3_file_path)
    
    if not success:
        print(f"Failed to convert {file_name}")
        return None
    
    # Now transcribe the file
    result = await transcribe_file(session, mp3_file_path, file_name)
    return result

async def convert_opus_to_mp3_async(path: str) -> TranscriptionList:
    """Convert opus files to mp3 and transcribe them concurrently"""
    transcriptions_list: TranscriptionList = []

    if not os.path.isdir(path):
        print(f"The specified path {path} does not exist or is not a directory.")
        return transcriptions_list
    
    if not api_key:
        print("Não foi detectada uma chave OPENAI")
        return []

    # Get all opus files
    opus_files = [f for f in os.listdir(path) if f.endswith('.opus')]
    
    async with aiohttp.ClientSession() as session:
        # Process each file (convert and transcribe) concurrently
        tasks = [process_file_async(session, file_name, path) for file_name in opus_files]
        results = await asyncio.gather(*tasks)
        
        # Filter out None results (failed conversions)
        transcriptions_list = [result for result in results if result]
    
    return transcriptions_list

def convert_opus_to_mp3(path: str) -> TranscriptionList:
    """Synchronous wrapper for the async function"""
    return asyncio.run(convert_opus_to_mp3_async(path))