from list_files import FileObj

def find_whats_key(data: list[FileObj]) -> str:
    for item in data:
        match item:
            case {'name': name} if 'WhatsApp' in name and name.endswith('.txt'):
                return name
            case {'name': name} if 'chat' in name and name.endswith('.txt'):
                return name

    raise ValueError("Neither 'whats' nor 'chat' were found in any item name")
