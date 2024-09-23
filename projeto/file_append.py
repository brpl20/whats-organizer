def file_appending(first_list, second_list):
    for item in second_list:
        for obj in first_list:
            if obj['FileAttached'] == item['FileName']:
                print('true')
                obj['AudioTranscription'] = item['Transcription']
                break
    return first_list

# def file_appending_pdf(first_list, second_list):
#     print(first_list)
#     print("===============================")
#     print(second_list)

def file_appending_pdf(messages, file_links):
    for message in messages:
        print(message)
        if message.get('FileAttached'):
            for file_info in file_links:
                print(file_info)
                if message['FileAttached'] == file_info['File']:
                    message['links'] = file_info['Links']
    return messages