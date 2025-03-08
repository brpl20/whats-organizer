from dataclasses import dataclass
import os
from typing import List, Optional, TypedDict

@dataclass(unsafe_hash=True)
class FileObj(TypedDict):
    name: Optional[str]
    size: Optional[int]
    whats: Optional[str]

def list_files_in_directory(directory_path: str):
    """
    Lists all files in the specified directory and returns a list of dictionaries.

    Each dictionary contains:
        - name (str): The name of the file.
        - size (int): The size of the file in bytes.

    Additionally, checks for a WhatsApp chat file (.txt) and prints a message if found or not.
    """

    file_list: List[FileObj] = []
    whatsapp_chat_found = False  # Flag to track WhatsApp chat

    try:
        for file in os.listdir(directory_path):
            file_path = os.path.join(directory_path, file)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)
                whats: Optional[str] = None
                name=file


                is_txt = file.endswith(".txt")
                chat_android = "WhatsApp" in file
                chat_ios = "_chat" in file
                if is_txt and (chat_android or chat_ios):
                    whatsapp_chat_found = True
                    whats=file
                
                file_info = FileObj(size=file_size, whats=whats, name=name)
                file_list.append(file_info)

    except FileNotFoundError:
        print(f"Error: Directory '{directory_path}' not found.")

    # why??
    if whatsapp_chat_found:
        print("WhatsApp chat found!")
    else:
        print("WhatsApp chat not found.")

    return file_list
