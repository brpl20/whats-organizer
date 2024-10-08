def find_whats_key(data):
    for item in data:
        if 'name' in item:
            if 'Whats' in item['name']:
                print("Found 'Whats' in name")
                return item['name']
            elif 'chat' in item['name']:
                print("Found 'chat' in name")
                return item['name']
    print("Error: Neither 'whats' nor 'chat' were found in any item name")
    raise ValueError("Neither 'whats' nor 'chat' were found in any item name")

