# app/main.py

from fastapi import FastAPI, WebSocket, UploadFile, File, Depends
from fastapi.responses import HTMLResponse
from app.stt import transcribe_audio_data
from app.tts import generate_speech
from groq import AsyncGroq
from openai import AsyncOpenAI

app = FastAPI()

async def get_groq_client() -> AsyncGroq:
    return AsyncGroq(api_key="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")


async def get_openai_client() -> AsyncOpenAI:
    return AsyncOpenAI(api_key="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")

@app.post("/stt")
async def stt_endpoint(file: UploadFile = File(...), groq_client: AsyncGroq = Depends(get_groq_client)):
    audio_data = await file.read()
    transcription = await transcribe_audio_data(audio_data, groq_client)
    return {"transcription": transcription}

@app.post("/tts")
async def tts_endpoint(text: str, openai_client: AsyncOpenAI = Depends(get_openai_client)):
    audio_data = await generate_speech(text, openai_client)
    return {"audio": audio_data}