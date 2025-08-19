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

def test_process_convo(test_zip_path, test_folder_name="test_run_1"):
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
    import sys
    
    # Get test file path from command line argument or use default
    if len(sys.argv) > 1:
        test_zip_path = sys.argv[1]
    else:
        # Use the provided test file path as default
        test_zip_path = "/home/brpl/code/whats-organizer-testing/android/teste-conversa-simples-sem-nada.zip"
    
    # Optional: get custom folder name from second argument
    test_folder_name = sys.argv[2] if len(sys.argv) > 2 else "test_run_1"
    
    # Check if file exists
    if not os.path.exists(test_zip_path):
        print(f"Error: Test file not found: {test_zip_path}")
        sys.exit(1)
    
    print(f"Testing with file: {test_zip_path}")
    print(f"Using folder name: {test_folder_name}")
    
    test_process_convo(test_zip_path, test_folder_name)