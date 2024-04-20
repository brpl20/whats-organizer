import re

def transform_to_html(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    html = ''
    speaker1_color = 'blue'
    speaker2_color = 'red'

    for line in lines:
        line = line.strip()
        if line.startswith('['):
            speaker = get_speaker(line)
            message = get_message(line)
            if '<anexado:' in message:
                file_name = get_file_name(message)
                file_html = get_file_html(file_name)
                html += f'<p><span style="color: {get_speaker_color(speaker)}">{speaker}: </span>{file_html}</p>'
            else:
                html += f'<p><span style="color: {get_speaker_color(speaker)}">{speaker}: </span>{message}</p>'

    return html

def get_speaker(line):
    return re.search(r'\[(.*?)\]', line).group(1)

def get_message(line):
    return line.split('] ')[1]

def get_file_name(message):
    return re.search(r'<anexado: (.*?)>', message).group(1)

def get_file_html(file_name):
    # Code to convert the file to HTML
    return f'<a href="{file_name}">Click here to view the file</a>'

def get_speaker_color(speaker):
    if speaker == 'Vinicius Bombinhas':
        return speaker1_color
    elif speaker == 'Ivete':
        return speaker2_color
    else:
        return 'black'

