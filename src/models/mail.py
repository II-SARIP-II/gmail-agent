from datetime import datetime

from pydantic import BaseModel, Field


class Mail(BaseModel):
    sender: str
    date: datetime
    subject: str
    message: str
    response: bool = Field(default=False)
