import logging

from fastapi import FastAPI

from controllers.chat_controller import router as chat_router


logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Internal Operations Agent")

app.include_router(chat_router)