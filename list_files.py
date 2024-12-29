import os 

def list_files_in_directory(directory_path):
    """
    Lists all files in the specified directory and returns a list of dictionaries.

    Each dictionary contains:
        - name (str): The name of the file.
        - size (int): The size of the file in bytes.

    Additionally, checks for a WhatsApp chat file (.txt) and prints a message if found or not.
    """

    file_list = []
    whatsapp_chat_found = False  # Flag to track WhatsApp chat

    try:
        for file in os.listdir(directory_path):
            file_path = os.path.join(directory_path, file)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)
                file_info = {
                    "name": file,
                    "size": file_size
                }
                file_list.append(file_info)

                # Check for WhatsApp chat
                if file.endswith(".txt") and "WhatsApp" in file:
                    whatsapp_chat_found = True
                    file_info_whats = {
                        "whats": file
                    }
                    file_list.append(file_info_whats) 

    except FileNotFoundError:
        print(f"Error: Directory '{directory_path}' not found.")

    # Print WhatsApp chat status after the loop
    if whatsapp_chat_found:
        print("WhatsApp chat found!")
    else:
        print("WhatsApp chat not found.")

    return file_list
