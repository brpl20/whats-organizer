import os
import subprocess

def convert_opus_to_mp3(file_locations):
    for file_item in file_locations:
        if isinstance(file_item, dict) and file_item.get('path', '').endswith(".opus"):
            file_path = file_item['path']
            output_file = file_path[:-5] + ".mp3"
            subprocess.run(['ffmpeg', '-i', file_path, '-acodec', 'libmp3lame', output_file])
            print(f"Converted {file_path} to {output_file}")
        elif isinstance(file_item, str) and file_item.endswith(".opus"):
            output_file = file_item[:-5] + ".mp3"
            subprocess.run(['ffmpeg', '-i', file_item, '-acodec', 'libmp3lame', output_file])
            print(f"Converted {file_item} to {output_file}")