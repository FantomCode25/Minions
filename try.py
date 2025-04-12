from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import os
import wave

# Initialize the Flask application
app = Flask(__name__)
app.config["SECRET_KEY"] = "secret_key"  # Replace with a secure secret key
socketio = SocketIO(app, cors_allowed_origins="*")  # Enable CORS for all origins

# Directory setup for saving files
AUDIO_DIR = "audio_files"
VIDEO_DIR = "video_frames"
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)

# Event handler for text input
@socketio.on("text")
def handle_text(data):
    """Handle incoming text messages."""
    print(f"Text received: {data}")
    emit("text_response", {"message": "Text received successfully!"})  # Acknowledge the client

# Event handler for audio input
@socketio.on("audio")
def handle_audio(data):
    """Handle incoming audio data."""
    print(f"Audio data received of length: {len(data)} bytes.")

    try:
        # Save audio data to a file
        filename = os.path.join(AUDIO_DIR, "received_audio.wav")
        with wave.open(filename, "wb") as audio_file:
            audio_file.setnchannels(1)  # Mono audio
            audio_file.setsampwidth(2)  # Sample width in bytes
            audio_file.setframerate(44100)  # Sample rate
            audio_file.writeframes(data)
        print("Audio file saved successfully!")
        emit("audio_response", {"message": "Audio saved successfully!"})  # Acknowledge the client
    except Exception as e:
        print(f"Error saving audio file: {e}")
        emit("audio_response", {"message": "Failed to save audio."})  # Notify the client

# Event handler for video input
@socketio.on("video")
def handle_video(data):
    """Handle incoming video frame data."""
    print(f"Video frame received of length: {len(data)} bytes.")

    try:
        # Save video frame as a JPEG file
        frame_path = os.path.join(VIDEO_DIR, "received_frame.jpeg")
        with open(frame_path, "wb") as video_file:
            video_file.write(data)
        print("Video frame saved successfully!")
        emit("video_response", {"message": "Video frame saved successfully!"})  # Acknowledge the client
    except Exception as e:
        print(f"Error saving video frame: {e}")
        emit("video_response", {"message": "Failed to save video frame."})  # Notify the client

# Run the Socket.IO server
if __name__ == "__main__":
    print("Starting the Socket.IO server...")
    socketio.run(app, host="0.0.0.0", port=8080)
