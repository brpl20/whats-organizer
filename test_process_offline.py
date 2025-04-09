# test_process.py
import os
from process_convo import process_convo

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
    test_zip_path = "./zip_tests/WhatsApp Chat - Adriana - Ap Country Riachuelo.zip"
    
    # Create a unique folder name for testing
    test_folder_name = "test_run_1"
    
    # Create mock file storage
    mock_file = MockFileStorage(test_zip_path)
    
    # Process the file
    result = process_convo(mock_file, test_folder_name, mock_notify_callback)
    
    # Print result or handle it as needed
    print("\nRESULT:")
    print(result)

if __name__ == "__main__":
    # Make sure you have a test_data directory with a WhatsApp ZIP file
    os.makedirs("./zip_tests/test_data", exist_ok=True)
    test_process_convo()