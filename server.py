import asyncio
import websockets
import wave

# Handle incoming connections
async def handle_connection(websocket):
    print("New client connected.")
    await websocket.send("Connection successful")
    await websocket.send("Hello from the server!")

    try:
        async for message in websocket:
            if isinstance(message, bytes):  # Check if the data is binary
                # Extract prefix and actual data
                prefix = message[:6].decode("utf-8")  # The first 6 bytes contain the prefix (e.g., "audio:" or "video:")
                data = message[6:]  # Remaining bytes are the actual data

                if prefix == "audio:":
                    print("Received audio data.")
                    handle_audio_blob(data)  # Process audio data
                elif prefix == "video:":
                    print("Received video data.")
                    handle_video_frame(data)  # Process video data
                else:
                    print("Unknown data type received.")
                    await websocket.send("Unknown data type received.")
            else:
                print("Invalid data format. Expected binary data.")
                await websocket.send("Invalid data format. Expected binary data.")
    except websockets.ConnectionClosed as e:
        print(f"Connection closed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        print("Client disconnected.")

# Process audio blobs
def handle_audio_blob(audio_blob):
    print("Processing audio data...")
    try:
        with wave.open("recorded_audio.wav", "wb") as audio_file:
            audio_file.setnchannels(1)  # Mono audio
            audio_file.setsampwidth(2)  # Sample width in bytes
            audio_file.setframerate(44100)  # Sample rate
            audio_file.writeframes(audio_blob)
        print("Audio data saved successfully!")
    except Exception as e:
        print(f"Error saving audio file: {e}")

# Forward video frames
def handle_video_frame(video_frame):
    print(f"Received video frame of size: {len(video_frame)} bytes")
    try:
        # Save the raw video frame to a file (optional for validation)
        with open("raw_video_frame.jpeg", "wb") as video_file:
            video_file.write(video_frame)
        print("Video frame successfully received and saved.")
        return True  # Indicates the frame is handled
    except Exception as e:
        print(f"Error handling video frame: {e}")
        return False

# Main function to start the server
async def main():
    async with websockets.serve(handle_connection, "localhost", 8080):
        print("WebSocket server running on ws://localhost:8080")
        await asyncio.Future()  # Keeps the server running indefinitely

if __name__ == "__main__":
    asyncio.run(main())
