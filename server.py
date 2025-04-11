import asyncio
import websockets
import wave
import os

async def handle_connection(websocket, path):
    async for message in websocket:
        # Example of saving binary audio data
        with open("audio.wav", "wb") as audio_file:
            audio_file.write(message)
        print("Audio data received and saved.")
        await websocket.send("Audio data processed!")
    print(f"WebSocket: {websocket}")
    print(f"Path: {path}")
    await websocket.send("Connection successful")

    await websocket.send("Hello from the server!")
    print("New client connected.")
    
    try:
        async for message in websocket:
            if not isinstance(message, bytes):
                await websocket.send("Invalid data format. Expected binary audio data.")
                continue

            print("Received audio data.")
            try:
                with wave.open("recorded_audio.wav", "wb") as audio_file:
                    audio_file.setnchannels(1)  # Mono audio
                    audio_file.setsampwidth(2)  # Sample width in bytes
                    audio_file.setframerate(44100)  # Sample rate
                    audio_file.writeframes(message)
                await websocket.send("Audio received and saved successfully!")
            except Exception as e:
                print(f"Error saving audio file: {e}")
                await websocket.send("Failed to save audio file.")
    except websockets.ConnectionClosed as e:
        print(f"Connection closed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        print("Client disconnected.")

async def main():
    async with websockets.serve(handle_connection, "localhost", 8080):
        print("WebSocket server running on ws://localhost:8080/ws")
        await asyncio.Future()  # Keeps the server running


if __name__ == "__main__":
    asyncio.run(main())


