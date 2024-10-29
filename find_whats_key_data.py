def find_whats_key(data):
    for item in data:
        if not 'name' in item:
            continue
        if 'Whats' in item['name']:
            print("Found 'Whats' in name")
            return item['name']
        if 'chat' in item['name']:
            print("Found 'chat' in name")
            return item['name']

    print("Error: Neither 'whats' nor 'chat' were found in any item name")
    raise ValueError("Neither 'whats' nor 'chat' were found in any item name")

