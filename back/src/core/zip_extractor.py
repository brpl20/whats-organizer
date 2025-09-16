import zipfile

def extract_zip_file(file_name, destination_folder):
    try:
        with zipfile.ZipFile(file_name, 'r') as zip_file:
            if destination_folder:
                zip_file.extractall(destination_folder)
                print(f"Files extracted to '{destination_folder}'")
            else:
                zip_file.extractall()
                print("Files extracted to the current directory")

    except FileNotFoundError:
        print(f"Error: File '{file_name}' not found.")
    except zipfile.BadZipFile:
        print(f"Error: '{file_name}' is not a valid ZIP file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
