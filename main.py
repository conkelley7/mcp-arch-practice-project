
from fastapi import FastAPI
from pydantic import BaseModel

from agent import run_agent

app = FastAPI(title="Internal Operations Agent")


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@app.post("/api/agent/chat")
async def chat(request: ChatRequest):
    response = await run_agent(request.message)

    return ChatResponse(response=response)
