def find_whats_key(data):
    whats_item = next((item['whats'] for item in data if 'whats' in item), None)
    return whats_item