import os
import subprocess
from dotenv import load_dotenv 
from openai import OpenAI


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
            opus_file_path = os.path.join(path, file_name)
            mp3_file_path = opus_file_path.replace('.opus', '.mp3')
            # @TODO verificar se tem falha de injeção de comando aqui
            command = ['sh', '-c', 'ffmpeg', '-i', opus_file_path, '-acodec', 'libmp3lame', mp3_file_path]
            try:
                subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                print(f"Converted {file_name} to MP3 format.")
                # WhisperTranscribe
                with open(mp3_file_path, 'rb') as f:
                    files = {'file': f}
                    transcript = client.audio.transcriptions.create(model="whisper-1",file=f)
                    add_transcription(file_name, transcript.text)
                    print("Transcrição...")
                    print(transcript.text)
            except subprocess.CalledProcessError as e:
                print(f"Failed to convert {file_name}. Error: {str(e)}")
    #pdb.set_trace()
    return transcriptions_list
