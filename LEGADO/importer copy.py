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

# Split the text into lines
lines = text.split("\n")

# Initialize variables to store the interlocutors
interlocutor1 = ""
interlocutor2 = ""

# Iterate through the lines
for line in lines:
    # Check if the line contains a colon (indicating a message)
    if ":" in line:
        # Split the line into the timestamp and the message
        timestamp, message = line.split(":", 1)
        
        # Extract the name of the interlocutor
        interlocutor = re.search(r"\[(.*?)\]", message).group(1)
        
        # Assign the interlocutor to the appropriate variable
        if interlocutor1 == "":
            interlocutor1 = interlocutor
        elif interlocutor2 == "":
            interlocutor2 = interlocutor

# Print the interlocutors
print("Interlocutor 1:", interlocutor1)
print("Interlocutor 2:", interlocutor2)
