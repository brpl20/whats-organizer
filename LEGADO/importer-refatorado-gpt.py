import re
import json

# Given text containing messages
text = """
[28/01/2020, 12:22:03] Vinicius Bombinhas: <anexado: 00000013-AUDIO-2020-01-28-12-22-03.opus>
[28/01/2020, 12:22:26] Ivete: Ok
[28/01/2020, 17:33:40] Ivete: Vinicius vc fez a lista dos aluguéis ?
[28/01/2020, 17:34:05] Ivete: Roberto me perguntou ?
[29/01/2020, 19:47:07] Ivete: Oi Vinícius . Faz 2  dias que estamos sem internet . Há algum problema  será?
[29/01/2020, 21:35:29] Vinicius Bombinhas: Vou  mandar mensagem na portaria
[17/02/2020, 17:48:47] Ivete: Vinicius boa tarde . Tudo bem Sei que vc está atrapalhado mas precisava dos depósitos . E também se o apto tá locado pro carnaval
[17/02/2020, 18:07:47] Vinicius Bombinhas: <anexado: 00000020-AUDIO-2020-02-17-18-07-47.opus>
[18/02/2020, 13:00:04] Vinicius Bombinhas: PELLIZETTI.pdf • 1 página <anexado: 00000021-PELLIZETTI.pdf>
[03/03/2020, 09:27:53] Ivete: Vinicius bom dia! Tudo bem?
[03/03/2020, 09:28:44] Ivete: Preciso que por favor me mande se há algum dia em que o apartamento esteja livre .
[03/03/2020, 09:30:21] Vinicius Bombinhas: Bom dia Ivete, vou verificar aqui
[03/03/2020, 09:30:42] Ivete: Outra coisa preciso que seu financeiro nos mande os depósitos. Acho que temos alguns valores em aberto
[03/03/2020, 15:01:34] Vinicius Bombinhas: <anexado: 00000026-PHOTO-2020-03-03-15-01-34.jpg>
[03/03/2020, 15:01:36] Vinicius Bombinhas: Mês de Março
[03/03/2020, 15:02:30] Vinicius Bombinhas: <anexado: 00000028-PHOTO-2020-03-03-15-02-30.jpg>
[03/03/2020, 15:15:35] Ivete: Desculpe não entendi estas datas . O verde e o que está locado ?
[03/03/2020, 15:15:42] Vinicius Bombinhas: Exato
[03/03/2020, 15:45:48] Ivete: Acha que podemos fazer isso?
"""

# Regular expression pattern to match date, time, sender, and message
pattern = re.compile(r'\[(\d{2}/\d{2}/\d{4}), (\d{2}:\d{2}:\d{2})\] (.*?):\s(.*?)<([^<>]+)>')

# List to store parsed messages
messages = []
current_speaker = None

# Parse each line of the text
for line in text.split("\n"):
    # Match the pattern
    match = pattern.match(line)
    if match:
        date, time, sender, message, attachment_name = match.groups()
        
        # Check if the sender has changed
        if sender != current_speaker:
            current_speaker = sender
            sender_id = len(messages) % 2 + 1  # Assign speaker ID
            
        messages.append({
            "date": date,
            "time": time,
            "sender": sender,
            "sender_id": sender_id,
            "message": message,
            "attachment_name": attachment_name
        })

# Create an HTML file
with open("/Users/brpl20/code/whats-organizer/messages.html", "w") as html_file:
    # Write the HTML header
    html_file.write("<html>\n<head>\n<style>\n")
    html_file.write(".speaker1 { color: blue; }\n")
    html_file.write(".speaker2 { color: green; }\n")
    html_file.write("</style>\n</head>\n<body>\n")
    
    # Loop through the messages and write them to the HTML file
    for message in messages:
        # Determine the CSS class based on the speaker_id
        css_class = "speaker1" if message['sender_id'] == 1 else "speaker2"
        
        # Write the message to the HTML file with the appropriate CSS class
        html_file.write(f"<p class='{css_class}'>{message['date']} {message['time']}</p>\n")
        html_file.write(f"<p class='{css_class}'>{message['sender']}:</p>\n")
        html_file.write(f"<p class='{css_class}'>{message['message']}</p>\n")
        
        # Check if there's an attachment
        if message['attachment_name']:
            html_file.write(f"<p class='{css_class}'>Attachment: {message['attachment_name']}</p>\n")

# Write the HTML footer

html_file.close()