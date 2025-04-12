from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import numpy as np
import librosa
import pyttsx3
import asyncio
import os
import tempfile
import wave
from groq import Client
import subprocess
from pydub import AudioSegment

# Set Groq API key
groq_client = Client(api_key="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")

# Initialize Flask app
app = Flask(__name__)
socketio = SocketIO(app)

# Set FFmpeg path
AudioSegment.converter = r"C:\Users\hp\Desktop\final1\ffmpeg-7.1.1\ffmpeg-7.1.1-essentials_build\bin\ffmpeg.exe"

# Check if FFmpeg is working correctly
try:
    subprocess.run([AudioSegment.converter, "-version"], check=True)
    print("FFmpeg is working correctly.")
except Exception as e:
    print(f"Error executing FFmpeg: {e}")

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

# WebSocket event to handle audio chunks
@socketio.on('audio_chunk')
def handle_audio_chunk(data):
    print("Received audio chunk.")
    try:
        # Process the received audio chunk
        audio_data = np.frombuffer(data, dtype=np.float32)
        audio_data = normalize_audio(audio_data)  # Normalize the audio
        audio_data = reduce_noise(audio_data)  # Reduce background noise

        # Analyze stress levels
        stress_level = analyze_stress(audio_data)
        print(f"Stress Level: {stress_level}")

        # Transcribe audio
        transcript = transcribe_audio(audio_data)
        print(f"Transcript: {transcript}")

        # Get AI response
        if isinstance(transcript, str) and transcript.strip():
            ai_response = asyncio.run(get_ai_response(transcript))
            print(f"AI Response: {ai_response}")

            # Convert AI response to speech
            temp_audio_path = os.path.join(tempfile.gettempdir(), "ai_response.wav")
            engine = pyttsx3.init()
            engine.save_to_file(ai_response, temp_audio_path)
            engine.runAndWait()

            # Read the audio file and send it back to the client
            with open(temp_audio_path, "rb") as audio_file:
                audio_data = audio_file.read()

            emit('transcription_update', {
                'transcript': transcript,
                'ai_response': ai_response,
                'audio': audio_data
            })
        else:
            print("Invalid transcript.")
            emit('transcription_update', {'transcript': 'Invalid transcript', 'ai_response': '', 'audio': None})
    except Exception as e:
        print(f"Error processing audio chunk: {e}")
        emit('transcription_update', {'transcript': 'Error processing audio', 'ai_response': '', 'audio': None})

# Flask route to handle audio processing
@app.route('/process_audio', methods=['POST'])
def process_audio():
    print("Request received at /process_audio")
    try:
        # Save the uploaded audio file
        audio_file = request.files['audio']
        temp_audio_path = os.path.join(tempfile.gettempdir(), "uploaded_audio.wav")
        audio_file.save(temp_audio_path)

        # Load the audio file
        audio_data, sr = librosa.load(temp_audio_path, sr=44100)

        # Process the audio file
        audio_data = normalize_audio(audio_data)  # Normalize the audio
        audio_data = reduce_noise(audio_data)  # Reduce background noise

        # Analyze stress levels
        stress_level = analyze_stress(audio_data)
        print(f"Stress Level: {stress_level}")

        # Transcribe audio
        transcript = transcribe_audio(audio_data)
        print(f"Transcript: {transcript}")

        # Get AI response
        if isinstance(transcript, str) and transcript.strip():
            ai_response = asyncio.run(get_ai_response(transcript))
            print(f"AI Response: {ai_response}")

            # Return the result
            return jsonify({"transcript": transcript, "ai_response": ai_response})
        else:
            print("Invalid transcript.")
            return jsonify({"transcript": "Invalid transcript", "ai_response": ""})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/process_saved_audio', methods=['POST'])
def process_saved_audio():
    print("Processing audio file from 'audio_files' directory...")
    try:
        # Specify the path to the audio file
        audio_file_name = request.json.get('file_name')  # Get the file name from the request
        if not audio_file_name:
            return jsonify({"error": "No file name provided"}), 400

        audio_file_path = os.path.join("audio_files", audio_file_name)

        # Check if the file exists
        if not os.path.exists(audio_file_path):
            return jsonify({"error": f"File '{audio_file_name}' not found in 'audio_files' directory"}), 404

        # Load the audio file
        audio_data, sr = librosa.load(audio_file_path, sr=44100)

        # Process the audio file
        audio_data = normalize_audio(audio_data)  # Normalize the audio
        audio_data = reduce_noise(audio_data)  # Reduce background noise

        # Analyze stress levels
        stress_level = analyze_stress(audio_data)
        print(f"Stress Level: {stress_level}")

        # Transcribe audio
        transcript = transcribe_audio(audio_data)
        print(f"Transcript: {transcript}")

        # Get AI response
        if isinstance(transcript, str) and transcript.strip():
            ai_response = asyncio.run(get_ai_response(transcript))
            print(f"AI Response: {ai_response}")

            # Convert AI response to speech
            temp_audio_path = os.path.join(tempfile.gettempdir(), "ai_response.wav")
            engine = pyttsx3.init()
            engine.save_to_file(ai_response, temp_audio_path)
            engine.runAndWait()

            # Read the audio file and send it back to the client
            with open(temp_audio_path, "rb") as audio_file:
                audio_data = audio_file.read()

            return jsonify({
                "transcript": transcript,
                "ai_response": ai_response,
                "audio": audio_data.decode("latin1")  # Encode binary data as a string
            })
        else:
            print("Invalid transcript.")
            return jsonify({"transcript": "Invalid transcript", "ai_response": "", "audio": None})
    except Exception as e:
        print(f"Error processing audio file: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("Starting Flask server...")
    socketio.run(app, host="127.0.0.1", port=5000, debug=False)



