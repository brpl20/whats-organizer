def file_appending(first_list, second_list):
    for item in second_list:
        for obj in first_list:
            if obj['FileAttached'] == item['FileName']:
                print('true')
                obj['AudioTranscription'] = item['Transcription']
                break
    return first_list