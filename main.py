import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
from PIL import Image, ImageTk
import speech_recognition as sr
import pyttsx3
import threading
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import json
import random

# Initialize speech recognition
recognizer = sr.Recognizer()
microphone = sr.Microphone()

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Initialize NLTK (you may need to download additional NLTK data)
nltk.download('punkt')
nltk.download('stopwords')

# Load intents and responses from JSON file
def load_intents(filename):
    with open(filename, 'r') as file:
        intents = json.load(file)
    return intents['intents']

intents = load_intents('intents.json')

# Function to recognize speech
def recognize_speech():
    with microphone as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        # Recognize speech using Google Speech Recognition
        query = recognizer.recognize_google(audio)
        print(f"User said: {query}")
        return query
    except sr.UnknownValueError:
        print("Could not understand audio.")
        return None
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        return None

# Function to process user query
def process_query(query):
    # Tokenization and stop word removal
    tokens = word_tokenize(query.lower())
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word.isalpha() and word not in stop_words]

    # Check each intent and return a random response
    for intent in intents:
        if any(pattern in tokens for pattern in intent['patterns']):
            return random.choice(intent['responses'])

    return "Sorry, I didn't understand that request."

# Function to speak the response
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to handle user interaction via microphone
def on_microphone_click():
    global mic_thread
    if not hasattr(on_microphone_click, 'mic_active') or not on_microphone_click.mic_active:
        on_microphone_click.mic_active = True
        mic_thread = threading.Thread(target=handle_microphone)
        mic_thread.start()
        # Update GUI to show microphone is active
        microphone_button.config(image=microphone_active_image)
        text_area.insert(tk.END, "Listening...\n")
    else:
        on_microphone_click.mic_active = False
        microphone_button.config(image=microphone_inactive_image)
        text_area.insert(tk.END, "Microphone turned off.\n")

# Function to handle microphone recognition
def handle_microphone():
    global mic_thread
    query = recognize_speech()
    if query:
        response = process_query(query)
        text_area.insert(tk.END, f"User: {query}\n")
        text_area.insert(tk.END, f"Assistant: {response}\n\n")
        speak(response)
    on_microphone_click.mic_active = False
    microphone_button.config(image=microphone_inactive_image)

# Function to handle user interaction via text entry
def on_click():
    query = entry.get()
    if query:
        response = process_query(query)
        text_area.insert(tk.END, f"User: {query}\n")
        text_area.insert(tk.END, f"Assistant: {response}\n\n")
        speak(response)

# Create GUI window
window = tk.Tk()
window.title("Virtual Assistant")

# Load microphone icons
microphone_active_img = Image.open("microphone_active.jpg").resize((30, 30), resample=Image.LANCZOS)
microphone_active_image = ImageTk.PhotoImage(microphone_active_img)
microphone_inactive_img = Image.open("microphone_inactive.jpg").resize((30, 30), resample=Image.LANCZOS)
microphone_inactive_image = ImageTk.PhotoImage(microphone_inactive_img)

# Create text area for conversation history
text_area = scrolledtext.ScrolledText(window, width=50, height=20, wrap=tk.WORD)
text_area.pack(padx=10, pady=10)

# Create entry field for user input
entry = tk.Entry(window, width=50)
entry.pack(padx=10, pady=(0, 10))

# Create button to submit user query
ask_button = tk.Button(window, text="Ask", command=on_click)
ask_button.pack(padx=10, pady=(0, 10))

# Create microphone button
microphone_button = tk.Button(window, image=microphone_inactive_image, command=on_microphone_click)
microphone_button.pack(side=tk.RIGHT, padx=10, pady=(0, 10))

# Main loop to run the GUI
if __name__ == "__main__":
    window.mainloop()
