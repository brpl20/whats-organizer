import os
import asyncio
from os.path import abspath
import subprocess
from subprocess import STDOUT, PIPE
from typing import List, TypedDict, TypeAlias, cast
import aiohttp
import json
from .sanitize import sanitize_path
from .config import config

class Transcription(TypedDict):
    FileName: str
    Transcription: str

TranscriptionList: TypeAlias = List[Transcription]


async def _transcribe_groq(session, mp3_file_path, file_name):
    """Transcribe using Groq Whisper (primary)"""
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {config.WHISPER_GROQ}"}

    with open(mp3_file_path, 'rb') as f:
        form_data = aiohttp.FormData()
        form_data.add_field('file', f.read(), filename=os.path.basename(mp3_file_path))
        form_data.add_field('model', 'whisper-large-v3-turbo')
        form_data.add_field('language', config.WHISPER_LANG)

        async with session.post(url, headers=headers, data=form_data) as response:
            result = await response.json()
            if response.status != 200:
                raise Exception(f"Groq API error ({response.status}): {result}")
            return result.get('text', '')


async def _transcribe_openai(session, mp3_file_path, file_name):
    """Transcribe using OpenAI Whisper (fallback)"""
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {config.WHISPER}"}

    with open(mp3_file_path, 'rb') as f:
        form_data = aiohttp.FormData()
        form_data.add_field('file', f.read(), filename=os.path.basename(mp3_file_path))
        form_data.add_field('model', 'whisper-1')
        form_data.add_field('language', config.WHISPER_LANG)

        async with session.post(url, headers=headers, data=form_data) as response:
            result = await response.json()
            if response.status != 200:
                raise Exception(f"OpenAI API error ({response.status}): {result}")
            return result.get('text', '')


async def transcribe_file(session, mp3_file_path, file_name):
    """Transcribe a file: Groq first, OpenAI fallback."""
    # Try Groq (primary)
    if config.WHISPER_GROQ:
        try:
            transcript = await _transcribe_groq(session, mp3_file_path, file_name)
            print(f"[Groq] Transcrição de {file_name}: {transcript}")
            return {'FileName': file_name, 'Transcription': transcript}
        except Exception as e:
            print(f"[Groq] Falhou para {file_name}: {e}")

    # Fallback to OpenAI
    if config.WHISPER:
        try:
            transcript = await _transcribe_openai(session, mp3_file_path, file_name)
            print(f"[OpenAI] Transcrição de {file_name}: {transcript}")
            return {'FileName': file_name, 'Transcription': transcript}
        except Exception as e:
            print(f"[OpenAI] Falhou para {file_name}: {e}")

    print(f"[Whisper] Nenhum provider disponível para {file_name}")
    return {'FileName': file_name, 'Transcription': ''}


async def convert_opus_to_mp3_async(path: str) -> TranscriptionList:
    """Convert opus files to mp3 and transcribe them concurrently"""
    transcriptions_list: TranscriptionList = []

    if not os.path.isdir(path):
        print(f"The specified path {path} does not exist or is not a directory.")
        return transcriptions_list

    if not config.WHISPER_GROQ and not config.WHISPER:
        print("Nenhuma chave de transcrição configurada (WHISPER_GROQ ou WHISPER)")
        return []

    # First convert all opus files to mp3
    conversion_tasks = []
    file_info = []

    print(f"Searching for audio files in: {path}")

    for file_name in os.listdir(path):
        if file_name.endswith('.opus'):
            # Use the path directly without adding cwd
            opus_file_path = os.path.join(path, file_name)
            mp3_file_path = opus_file_path.replace('.opus', '.mp3')
            opus_file_path = sanitize_path(opus_file_path)
            mp3_file_path = sanitize_path(mp3_file_path)

            print(f"Found audio file: {file_name}")
            print(f"Converting {opus_file_path} to {mp3_file_path}")

            command = ['ffmpeg', '-y', '-i', opus_file_path, '-acodec', 'libmp3lame', mp3_file_path]
            process = subprocess.Popen(command, stdout=PIPE, stderr=STDOUT, text=True)
            conversion_tasks.append(process)
            file_info.append((file_name, mp3_file_path))

    # Wait for all conversions to complete
    for process in conversion_tasks:
        stdout, stderr = process.communicate()
        if int(process.returncode or 0):
            print(f"[{process.returncode}] Failed to convert a file.\n\n{stdout}\n\n{stderr}")
            return transcriptions_list

    if not file_info:
        print("No .opus audio files found to transcribe")
        return transcriptions_list

    # Now transcribe all mp3 files concurrently
    provider = "Groq" if config.WHISPER_GROQ else "OpenAI"
    print(f"Transcribing {len(file_info)} audio files (primary: {provider})...")
    async with aiohttp.ClientSession() as session:
        transcription_tasks = []
        for file_name, mp3_file_path in file_info:
            task = transcribe_file(session, mp3_file_path, file_name)
            transcription_tasks.append(task)

        transcriptions = await asyncio.gather(*transcription_tasks)
        transcriptions_list.extend(transcriptions)

    print(f"Successfully transcribed {len(transcriptions_list)} files")
    return transcriptions_list

def convert_opus_to_mp3(path: str) -> TranscriptionList:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(convert_opus_to_mp3_async(path))
    else:
        future = asyncio.run_coroutine_threadsafe(convert_opus_to_mp3_async(path), loop)
        return future.result()
