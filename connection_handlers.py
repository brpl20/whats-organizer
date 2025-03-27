import os
import shutil
from typing import Optional

def cleanup_files(unique_folder_name: str) -> None:
    """Clean up temporary files after processing"""
    base_folder = "./zip_tests/"
    final_work_folder = os.path.join(base_folder, unique_folder_name)
    
    if os.path.exists(final_work_folder):
        try:
            # Delete the folder and all its contents
            shutil.rmtree(final_work_folder)
            print(f"Successfully deleted temporary folder: {final_work_folder}")
        except Exception as e:
            print(f"Error deleting folder: {e}")
    else:
        print(f"Folder does not exist: {final_work_folder}")

