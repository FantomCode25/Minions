import cv2
from deepface import DeepFace
import datetime
import csv
import os
import pyttsx3

# TTS engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)

emotion_messages = {
    "happy": "You look happy! Keep smiling 😊",
    "sad": "It's okay to feel sad. You're not alone 💙",
    "angry": "Take a deep breath, you're stronger than your anger 😌",
    "surprise": "Something surprised you? Hope it's good! 🌟",
    "fear": "It's okay to be scared. You're safe now 🤗",
    "disgust": "Ugh! Something grossed you out? 😅",
    "neutral": "You're calm and composed. Sending peace your way 🧘‍♀️"
}

def speak(message):
    engine.say(message)
    engine.runAndWait()

def log_to_csv(username, emotion, timestamp):
    file_exists = os.path.isfile("user_data.csv")
    with open("user_data.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Username", "Timestamp", "Emotion"])
        writer.writerow([username, timestamp, emotion])

def detect_emotion_and_log(frame, username):
    try:
        result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
        dominant_emotion = result[0]['dominant_emotion']
        message = emotion_messages.get(dominant_emotion, "You are unique ❤️")
        
        # Log the emotion
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_to_csv(username, dominant_emotion, timestamp)
        
        # Speak the message
        speak(message)

        return dominant_emotion.capitalize(), message
    except Exception as e:
        return "Error", "Couldn't detect emotion. Try again."
