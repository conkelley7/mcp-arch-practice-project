import logging

from fastapi import APIRouter, HTTPException

from agent import run_agent
from schemas.chat import ChatRequest, ChatResponse


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/agent",
    tags=["Agent"],
)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    try:
        response = await run_agent(request.message)
        return ChatResponse(response=response)

    except Exception:
        logger.exception("Agent request failed")

        raise HTTPException(
            status_code=502,
            detail="The agent could not complete the request.",
        ) from None