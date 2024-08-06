import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from chat_session import ChatSession
from thread_manager import ThreadManager
from assistant_manager import AssistantManager
from async_openai_client import AsyncOpenAIClient  # Ensure this import is correct

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

app = FastAPI()

API_KEY = "your_api_key_here"
ASSISTANT_NAME = "your_assistant_name_here"
MODEL_NAME = "your_model_name_here"

async def create_managers():
    try:
        client = AsyncOpenAIClient(api_key=API_KEY)
        thread_manager = ThreadManager(client=client)
        assistant_manager = AssistantManager(client=client)
        chat_session = ChatSession(thread_manager, assistant_manager, ASSISTANT_NAME, MODEL_NAME)
        return chat_session
    except Exception as e:
        logging.error(f"Error in create_managers: {e}")
        raise

@app.post("/chat/", response_model=ChatResponse)
async def handle_chat(request: ChatRequest):
    try:
        chat_session = await create_managers()
        response = await chat_session.get_latest_response(request.message)
        if response:
            return ChatResponse(response=response)
        raise HTTPException(status_code=500, detail="Error generating response")
    except Exception as e:
        logging.error(f"Error in handle_chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))
