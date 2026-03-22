import speech_recognition as sr
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Adjusting for background noise...")
        r.adjust_for_ambient_noise(source, duration=1)
        r.pause_threshold = 2.5  # seconds of silence before stopping
        r.non_speaking_duration = 0.5  # minimum silence duration
        print("Speak now...")
        audio = r.listen(source)
    
    try:
        text = r.recognize_google(audio, language="hy-AM")
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Could not understand audio")
        return None
    except sr.RequestError as e:
        print(f"Error: {e}")
        return None
