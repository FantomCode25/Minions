import os
import openai
import asyncio
import websockets
import numpy as np
import librosa
import soundfile as sf
import speech_recognition as sr
from fastapi import FastAPI, WebSocket
from transformers import pipeline
from tensorflow.keras.models import load_model
from utils.emotion_recognition import predict_emotion

app = FastAPI()

# OpenAI GPT-4 API Key (Replace with actual key)
openai.api_key = "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"

# Load trained emotion detection model
emotion_model = load_model("emotion_model.h5")

# Load sentiment analysis model
sentiment_analyzer = pipeline("sentiment-analysis")

def extract_audio_features(file_path):
    """
    Extracts audio features for emotion detection.
    """
    y, sr = librosa.load(file_path, sr=16000)
    features = {
        "chroma_stft": np.mean(librosa.feature.chroma_stft(y=y, sr=sr)),
        "rms": np.mean(librosa.feature.rms(y=y)),
        "spectral_centroid": np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)),
        "spectral_bandwidth": np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr)),
        "rolloff": np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr)),
        "zero_crossing_rate": np.mean(librosa.feature.zero_crossing_rate(y)),
    }
    return features

@app.websocket("/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    recognizer = sr.Recognizer()

    while True:
        try:
            # Receive audio file from client
            audio_data = await websocket.receive_bytes()
            
            # Save temporary file
            file_location = "temp_audio.wav"
            with open(file_location, "wb") as f:
                f.write(audio_data)

            # Convert audio to text
            with sr.AudioFile(file_location) as source:
                audio = recognizer.record(source)
                try:
                    user_text = recognizer.recognize_google(audio)
                except sr.UnknownValueError:
                    user_text = "I couldn't understand that."

            # Analyze sentiment from text
            sentiment = sentiment_analyzer(user_text)[0]

            # Detect emotions from voice
            voice_emotion = predict_emotion(file_location)

            # Get response from GPT-4
            response = generate_gpt_response(user_text, sentiment, voice_emotion)

            # Send response back to the client
            await websocket.send_text(response)

            # Cleanup
            os.remove(file_location)

        except Exception as e:
            await websocket.send_text(f"Error: {str(e)}")
            break

def generate_gpt_response(user_text, sentiment, voice_emotion):
    """
    Generates a conversational response using GPT-4.
    """
    prompt = f"You are a kind and empathetic friend. The user is feeling {sentiment['label'].lower()} based on text and {voice_emotion.lower()} based on voice tone. They said: '{user_text}'. Respond like a caring friend."
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a friendly, supportive chatbot."},
                  {"role": "user", "content": prompt}]
    )

    return response['choices'][0]['message']['content']
