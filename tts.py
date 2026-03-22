from openai import OpenAI
import pygame
import tempfile
import os
from dotenv import load_dotenv
load_dotenv()

client = OpenAI()

def speak(text):
    response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=text
    )
    
    with tempfile.NamedTemporeanFile(delete=False, suffix=".mp3") as f:
        f.write(response.content)
        temp_file = f.name
    
    pygame.mixer.init()
    pygame.mixer.music.load(temp_file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.music.unload()
    os.remove(temp_file)
