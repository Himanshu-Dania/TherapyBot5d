import sys
import os

# Points to the parent directory containing EmotionBot, StrategyBot, TherapyBot
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
import asyncio
import torch
from transformers import pipeline
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
import json
from TherapyBot.chatbot_stream import Chatbot

app = FastAPI()

# Instantiate chatbot instance globally
chatbot = Chatbot()

# Global variable to store the last user message
chat_store = None


@app.get("/")
async def home():
    """Serve the static HTML file"""
    with open("static/chatbot_stream.html", "r") as f:
        return HTMLResponse(content=f.read())


@app.post("/chat")
async def chat(request: Request):
    """Handles the user message submission."""
    global chat_store  # Use global variable
    data = await request.json()
    user_message = data.get("message", "")
    print(f"Received message: {user_message}")

    # Store the user message in the global variable
    chat_store = user_message

    return {"message": "Message received", "status": "OK"}


@app.get("/chat-stream")
async def chat_stream():
    """Streams the bot's response for the user's message."""
    if chat_store is None:
        return {"error": "No message received yet"}

    print(f"Last message: {chat_store}")

    async def stream_response():
        try:
            response = ""
            # Start streaming the response from chatbot.gemini using the chat_store message
            async for token in chatbot.gemini(chat_store):
                # If the token is different from the last one (to avoid repetition)
                if token != response:
                    # Append the new token to the response
                    response = token
                    yield f"data: {response}\n\n"

            # Optionally send a signal to the frontend that the stream has ended
            yield "data: [END]\n\n"  # End signal to stop stream logic, not shown in frontend

        except Exception as e:
            yield f"data: Error occurred: {str(e)}\n\n"

    return StreamingResponse(stream_response(), media_type="text/event-stream")
