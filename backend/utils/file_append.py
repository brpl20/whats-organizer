def file_appending(first_list, second_list):
    """
    Append transcriptions to messages
    
    Args:
        first_list: List of messages with 'FileAttached' field
        second_list: List of transcriptions with 'FileName' and 'Transcription' fields
    """
    print(f"Appending {len(second_list)} transcriptions to {len(first_list)} messages")
    
    matched_count = 0
    for item in second_list:
        for obj in first_list:
            # Check if FileAttached field exists and matches
            if obj.get('FileAttached'):
                # Match both with and without extension changes (.opus -> .mp3)
                file_attached = obj['FileAttached']
                file_name = item['FileName']
                
                # Try direct match or with extension replacement
                if (file_attached == file_name or
                    file_attached.replace('.mp3', '.opus') == file_name or
                    file_attached == file_name.replace('.opus', '.mp3')):
                    
                    print(f"Matched transcription for: {file_attached}")
                    obj['AudioTranscription'] = item['Transcription']
                    matched_count += 1
                    break
    
    print(f"Successfully matched {matched_count} transcriptions")
    return first_list

# def file_appending_pdf(first_list, second_list):
#     print(first_list)
#     print("===============================")
#     print(second_list)

def file_appending_pdf(messages, file_links):
    for message in messages:
        if message.get('FileAttached'):
            for file_info in file_links:
                if message['FileAttached'] == file_info['File']:
                    message['links'] = file_info['Links']
    return messages