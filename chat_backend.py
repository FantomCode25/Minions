from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Allow frontend to access backend (important for local dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with ["http://localhost:8080"] for tighter security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatInput(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(input: ChatInput):
    user_message = input.message
    print("User said:", user_message)

    # Replace this with your actual chatbot logic (e.g., GPT, Rasa, etc.)
    response = f"You said: {user_message}"
    return {"response": response}
