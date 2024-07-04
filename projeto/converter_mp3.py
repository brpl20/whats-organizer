import os
import subprocess

# Directory containing .opus files
path = os.path.join(os.getcwd(), 'whats')
input_directory = path
output_directory = path

# Iterate over files in the input directory
for filename in os.listdir(input_directory):
    if filename.endswith(".opus"):
        # Construct input and output file paths
        input_file = os.path.join(input_directory, filename)
        output_file = os.path.join(output_directory, os.path.splitext(filename)[0] + ".mp3")
        
        # Run ffmpeg command to convert .opus to .mp3
        subprocess.run(['ffmpeg', '-i', input_file, '-acodec', 'libmp3lame', output_file])
        
        print(f"Converted {input_file} to {output_file}")
