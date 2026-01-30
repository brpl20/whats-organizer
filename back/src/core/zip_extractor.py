import os
import zipfile


def extract_zip_file(file_name, destination_folder):
    try:
        with zipfile.ZipFile(file_name, 'r') as zip_file:
            dest = destination_folder or '.'
            for info in zip_file.infolist():
                # Fix filename encoding: Python uses CP437 when UTF-8 flag is not set,
                # but WhatsApp ZIPs contain UTF-8 filenames (accented chars like ó, é).
                if not (info.flag_bits & 0x800):  # UTF-8 flag not set
                    try:
                        fixed_name = info.filename.encode('cp437').decode('utf-8')
                    except (UnicodeDecodeError, UnicodeEncodeError):
                        fixed_name = info.filename
                else:
                    fixed_name = info.filename

                target_path = os.path.join(dest, fixed_name)
                if info.is_dir():
                    os.makedirs(target_path, exist_ok=True)
                else:
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    with zip_file.open(info) as src, open(target_path, 'wb') as dst:
                        dst.write(src.read())

            print(f"Files extracted to '{dest}'")

    except FileNotFoundError:
        print(f"Error: File '{file_name}' not found.")
    except zipfile.BadZipFile:
        print(f"Error: '{file_name}' is not a valid ZIP file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
