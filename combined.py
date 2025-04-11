from flask import Flask, request, jsonify
from flask_socketio import SocketIO
import asyncio
import websockets
import wave
import requests
import threading
import os
import tempfile

# Flask app setup
app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/process_audio', methods=['POST'])
def process_audio():
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

# WebSocket server setup
async def handle_connection(websocket):
    print("New client connected.")
    await websocket.send("Connection successful")
    
    try:
        async for message in websocket:
            # Validate message format
            if not isinstance(message, bytes):
                await websocket.send("Invalid data format. Expected binary audio data.")
                continue
            
            print("Received audio data.")
            try:
                # Save audio file locally
                audio_file_path = "recorded_audio.wav"
                with wave.open(audio_file_path, "wb") as audio_file:
                    audio_file.setnchannels(1)  # Mono audio
                    audio_file.setsampwidth(2)  # Sample width in bytes
                    audio_file.setframerate(44100)  # Sample rate
                    audio_file.writeframes(message)  # Write the audio data
                
                print("Sending audio file to Flask server...")
                # Send audio file to Flask server for processing
                with open(audio_file_path, "rb") as audio_file:
                    response = requests.post(
                        "http://127.0.0.1:5000/process_audio",  # Flask server URL
                        files={"audio": audio_file}
                    )
                
                # Handle response from Flask server
                if response.status_code == 200:
                    result = response.json()
                    print(f"Processing result: {result}")
                    await websocket.send(f"Processing result: {result}")
                else:
                    print(f"Error from Flask server: {response.text}")
                    await websocket.send("Error processing audio.")
            except Exception as e:
                print(f"Error handling audio file: {e}")
                await websocket.send("Failed to process audio file.")
    except websockets.ConnectionClosed as e:
        print(f"Connection closed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        print("Client disconnected.")

async def websocket_server():
    async with websockets.serve(handle_connection, "localhost", 8080):
        print("WebSocket server running on ws://localhost:8080")
        await asyncio.Future()  # Keeps the server running indefinitely

# Threading to run both servers
def run_flask():
    print("Starting Flask server...")
    socketio.run(app, host="127.0.0.1", port=5000, debug=False)

def run_websocket():
    print("Starting WebSocket server...")
    asyncio.run(websocket_server())

if __name__ == "__main__":
    # Create threads for Flask and WebSocket servers
    flask_thread = threading.Thread(target=run_flask)
    websocket_thread = threading.Thread(target=run_websocket)

    # Start both threads
    flask_thread.start()
    websocket_thread.start()

    # Wait for both threads to complete
    flask_thread.join()
    websocket_thread.join()