import zipfile
import os

def list_files(folder):
    zip_files = []
    for file in os.listdir(folder):
        if file.endswith('.zip'):
            zip_files.append(file)
    if len(zip_files) == 1:
        return zip_files[0]
    else:
        return zip_files

def open_file(file):
    with zipfile.ZipFile(file, 'r') as zip_ref:
        zip_ref.extractall()
        zip_path = os.path.join(os.getcwd(), file)
        return zip_path

def read_file(pathfile):
    with open(pathfile, 'r') as file:
        print(file)
