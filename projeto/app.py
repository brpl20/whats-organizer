from flask import Flask, request, jsonify
from flask_cors import CORS

import uuid
import json
import os

# Import your existing functions
from handle_zip_file import handle_zip_file
from list_files import list_files_in_directory
from find_whats_key_data import find_whats_key
from extract_device import extract_info_device
from file_fixer import process_file_fixer 
from extract_objects_v2 import extract_info_iphone, extract_info_android
from converter_mp3 import convert_opus_to_mp3
from file_append import file_appending

app = Flask(__name__)
CORS(app)
@app.route('/process', methods=['POST'])
def process_zip():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and file.filename.endswith('.zip'):
        # Create a unique working directory
        base_folder = "./zip_tests/"
        unique_folder_name = str(uuid.uuid4())
        final_work_folder = os.path.join(base_folder, unique_folder_name)
        os.makedirs(final_work_folder, exist_ok=True)
        
        # Save the uploaded file
        zip_path = os.path.join(final_work_folder, "uploaded.zip")
        file.save(zip_path)
        
        # Process the zip file
        handle_zip_file(zip_path, final_work_folder)
        
        # List objects in the directory
        file_object = list_files_in_directory(final_work_folder)
        
        # Convert MP3 and transcribe
        transcriptions = convert_opus_to_mp3(final_work_folder)
        
        # Extract main conversation
        whats_main_file = find_whats_key(file_object)
        whats_main_folder_file = os.path.join(final_work_folder, whats_main_file)
        
        # Extract device info
        dispositivo = extract_info_device(whats_main_folder_file)
        
        # Fix files
        fixed_file = process_file_fixer(whats_main_folder_file, dispositivo)
        
        # Extract info based on device type
        if dispositivo == "android":
            extracted_info = extract_info_android(fixed_file)
        elif dispositivo == "iphone":
            extracted_info = extract_info_iphone(fixed_file)
        else:
            return jsonify({"error": "Unknown device type"}), 400
        
        # Append files
        list_files = file_appending(extracted_info, transcriptions)
        
        # Create JSON output
        output_path = os.path.join(final_work_folder, 'output.json')
        with open(output_path, 'w') as f:
            json.dump(list_files, f)
        
        # Read the JSON file and return its contents
        with open(output_path, 'r') as f:
            result = json.load(f)
        
        return jsonify(result)
    
    return jsonify({"error": "Invalid file format"}), 400

if __name__ == '__main__':
    app.run(debug=True)