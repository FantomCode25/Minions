import cv2
import random

# Load Haar Cascade
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

# Emotion map
emotions = ["happy", "sad", "angry", "surprise", "neutral"]
emotion_messages = {
    "happy": "You look happy! Keep smiling 😊",
    "sad": "It's okay to feel sad. You're not alone 💙",
    "angry": "Take a deep breath, you're stronger than your anger 😌",
    "surprise": "Something surprised you? Hope it's good! 🌟",
    "neutral": "You're calm and composed. Sending peace your way 🧘‍♀️"
}

# Detect emotion function
def detect_emotion(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    if len(faces) == 0:
        return "No Face Detected", "Please try again!"

    # Take the first face detected
    (x, y, w, h) = faces[0]
    face_roi = gray[y:y+h, x:x+w]

    # Simulated prediction
    predicted_emotion = random.choice(emotions)
    return predicted_emotion, emotion_messages[predicted_emotion]
