from openai import OpenAI
client = OpenAI(api_key="")


audio_file = open("/Users/brpl20/code/whats-organizer/projeto/zip_tests/84fc2d28-3162-473f-9bb3-d7955cf14258/00000937-AUDIO-2023-05-22-17-39-37.mp3", "rb")
transcript = client.audio.transcriptions.create(
  model="whisper-1",
  file=audio_file
)
print(transcript.text)