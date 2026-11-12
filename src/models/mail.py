from datetime import datetime

from pydantic import BaseModel, Field


class Mail(BaseModel):
    id: str
    sender: str
    date: datetime
    subject: str
    message: str
    attachment: list[str]
    to_answer: bool = Field(default=False)
    response1: str = Field(default="")
    response2: str = Field(default="")
    to_send: bool = Field(default=False)
