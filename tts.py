# app/tts.py

from openai import AsyncOpenAI

async def generate_speech(text: str, client: AsyncOpenAI) -> bytes:
    response = await client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )
    return response.content