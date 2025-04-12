from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import sounddevice as sd
import numpy as np
import librosa
import pyttsx3
import asyncio
import os
import tempfile
import wave
from groq import Client

# Set Groq API key
groq_client = Client(api_key="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")

# Initialize Flask app
app = Flask(__name__)
socketio = SocketIO(app)

# Function to record audio
def record_audio(duration=5, fs=44100):
    """Record audio for a given duration."""
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    return audio.flatten()

# Function to normalize audio
def normalize_audio(audio_data):
    """Normalize audio to have values between -1 and 1."""
    return audio_data / np.max(np.abs(audio_data))

# Function to reduce noise
def reduce_noise(audio_data, sr=44100):
    """Reduce background noise using spectral gating."""
    noise_profile = librosa.effects.split(audio_data, top_db=20)
    return librosa.effects.remix(audio_data, intervals=noise_profile)

# Function to analyze stress levels using Librosa
def analyze_stress(audio_data, sr=44100):
    """Analyze stress levels using MFCC features."""
    mfccs = librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=13)
    return np.mean(mfccs)

# Function to transcribe audio using Groq
def transcribe_audio(audio_data, target_sr=16000):
    """Transcribe audio using Groq's Whisper model."""
    audio_data = librosa.resample(audio_data, orig_sr=44100, target_sr=target_sr)
    temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    wav_path = temp_wav.name
    temp_wav.close()

    with wave.open(wav_path, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(target_sr)
        wav_file.writeframes((audio_data * 32767).astype(np.int16))

    with open(wav_path, 'rb') as audio_file:
        response = groq_client.audio.transcriptions.create(
            model="whisper-large-v3-turbo",
            file=audio_file,
            response_format="text"
        )
    return response

# Function to get AI response from Groq
async def get_ai_response(transcript):
    """Get AI response from Groq."""
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": transcript}
        ],
        temperature=0,
        max_tokens=500
    )
    return response.choices[0].message.content

# Function for text-to-speech
def text_to_speech(text):
    """Convert text to speech."""
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# Main function to connect everything
async def main():
    # Step 1: Record audio
    audio_data = record_audio(duration=5)
    audio_data = normalize_audio(audio_data)  # Normalize the audio
    audio_data = reduce_noise(audio_data)  # Reduce background noise

    # Step 2: Analyze stress levels
    stress_level = analyze_stress(audio_data)
    print(f"Stress Level: {stress_level}")

    # Step 3: Convert audio to text
    transcript = transcribe_audio(audio_data)  # Call without await
    print(f"Transcript: {transcript}")

    # Check if the transcript is valid
    if isinstance(transcript, str) and transcript.strip():
        # Step 4: Get AI response
        ai_response = await get_ai_response(transcript)
        print(f"AI Response: {ai_response}")

        # Step 5: Convert AI response to speech
        text_to_speech(ai_response)
    else:
        print("Invalid transcript. Please try again.")

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())

# WebSocket event to handle audio chunks
@socketio.on('connect')
def handle_connect():
    print("WebSocket client connected.")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected.")

@socketio.on('audio_chunk')
def handle_audio_chunk(data):
    print("Received audio chunk.")
    emit('transcription_update', {'transcript': 'Processing...', 'ai_response': '...'})

@socketio.on('recording_stopped')
def handle_recording_stopped():
    print("Recording stopped.")
    emit('transcription_update', {'transcript': 'Final transcript', 'ai_response': 'Final AI response'})

# Flask route to handle audio processing
@app.route('/process_audio', methods=['POST'])
def process_audio():
    print("Request received at /process_audio")
    try:
        # Save the uploaded audio file
        audio_file = request.files['audio']
        temp_audio_path = os.path.join(tempfile.gettempdir(), "uploaded_audio.wav")
        audio_file.save(temp_audio_path)

        # Process the audio file (e.g., transcription, AI response)
        transcript = "This is a placeholder transcript."
        ai_response = "This is a placeholder AI response."

        # Return the result
        return jsonify({"transcript": transcript, "ai_response": ai_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("Starting Flask server...")
    socketio.run(app, host="127.0.0.1", port=5000, debug=False)



