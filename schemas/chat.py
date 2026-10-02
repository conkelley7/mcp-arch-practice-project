from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)

    @field_validator("message")
    @classmethod
    def reject_blank_message(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Message cannot be blank.")

        return value


class ChatResponse(BaseModel):
    response: str