# test_process_offline.py
import os
from process_convo import process_convo
from flask import Flask

class MockFileStorage:
    def __init__(self, path):
        self.path = path
        
    def save(self, destination):
        with open(self.path, 'rb') as src_file:
            with open(destination, 'wb') as dest_file:
                dest_file.write(src_file.read())

def mock_notify_callback(message):
    print(f"STATUS: {message}")

def test_process_convo():
    # Path to your test ZIP file
    test_zip_path = "./zip_tests/android1.zip"
    
    # Create a unique folder name for testing
    test_folder_name = "test_run_1"
    
    # Create mock file storage
    mock_file = MockFileStorage(test_zip_path)
    
    # Create a Flask app context
    app = Flask(__name__)
    with app.app_context():
        # Process the file
        response = process_convo(mock_file, test_folder_name, mock_notify_callback)
        
        # Extract data from the Response object
        result_data = response.get_json()
        
        # Print result
        print("\nRESULT:")
        if result_data:
            print(result_data)
        else:
            print(f"Response: {response}")
            print(f"Response data: {response.data}")

if __name__ == "__main__":
    # Make sure you have a test_data directory with a WhatsApp ZIP file
    os.makedirs("./zip_tests/test_data", exist_ok=True)
    test_process_convo()