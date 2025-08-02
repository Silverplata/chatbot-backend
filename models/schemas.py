from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class ChatRequest(BaseModel):
    question: str
    max_tokens: Optional[int] = 2000

class ColorPalette(BaseModel):
    primary_color: str
    secondary_color: str
    accent_color: str
    background_color: str

class User(BaseModel):
    username: str
    primary_color: str
    secondary_color: str
    accent_color: str
    background_color: str