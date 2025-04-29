import speech_recognition as sr
import pyautogui
import base64
import requests
import time
from functools import wraps
import pyttsx3

import os

def timer(func):
    """Decorator that prints the execution time of the decorated function."""
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()  # High precision timer
        result = func(*args, **kwargs)    # Execute the decorated function
        end_time = time.perf_counter()
        
        elapsed_time = end_time - start_time
        print(f"Function '{func.__name__}' executed in {elapsed_time:.2f} seconds")
        return result
    
    return wrapper


def speech_to_text() -> str | None:
    # Initialize the recognizer
    recognizer = sr.Recognizer()
    # Use the default microphone as the audio source
    with sr.Microphone() as source:
        print("Listening... Speak now!")
        # Adjust for ambient noise
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            # Listen to the microphone input
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            print("Processing your speech...")
            # Use Sphinx (offline recognizer)
            text = recognizer.recognize_sphinx(audio)
            print("\nSpeech Recognition Results:")
            print(f": {text}")
            return text
        except sr.WaitTimeoutError:
            print("Listening timed out. No speech detected.")
            return None
        except sr.UnknownValueError:
            print("Could not understand the audio.")
            return None
        except sr.RequestError as e:
            print(f"Recognition error: {e}")
            return None


def capture(filename: str = "screenshot.png") -> str:
    img = pyautogui.screenshot()
    img.save(filename)
    return filename


def encode_image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


@timer
def call_llm(prompt_text: str, image_path: str, system_prompt: str, model="gemma3") -> str:
    image_base64 = encode_image_to_base64(image_path)
    payload = {
        "model": model,
        "prompt": f"{system_prompt}\nUser Prompt: {prompt_text}",
        "images": [image_base64],
        "stream": False
    }
    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload)
        if response.status_code == 200:
            return response.json().get("response", "")
        return f"LLM Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"Error contacting LLM: {str(e)}"


def text_to_speech(text):
    if text:
        # Initialize the text-to-speech engine
        engine = pyttsx3.init()
        # Set properties (optional)
        engine.setProperty('rate', 170)  # Speed of speech
        engine.setProperty('volume', 0.9)  # Volume level
        print("\nSpeaking the text...")
        engine.say(text)
        engine.runAndWait()
        engine.stop()


if __name__ == "__main__":
    # >> For transcribing text
    transcribed_text = speech_to_text()

    # >> For taking screenshot
    print("📸 Taking screenshot...")
    path = capture()
    print(f"Saved to {path}")
    # path = f'firefox_full_20250428_145317.png'

    # >> For calling LLM 
    SYSTEM_PROMPT = "You are a helpful visual accessibility agent. Describe images clearly, concisely, and objectively in a sentence. Focus only on what is visually present without assuming unobservable details. Your explanations must be easy to understand."
    # USER_PROMPT = "Briefly describe the visible contents of this image in points."
    USER_PROMPT = "What is the image?"#transcribed_text
    IMAGE_PATH = path
    print("Sending to LLM...")
    result = call_llm(USER_PROMPT, IMAGE_PATH, SYSTEM_PROMPT)
    print("LLM Response:\n", result)
    
    #>> For text to speech
    if result:
        text_to_speech(result)