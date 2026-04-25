from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List


class SessionCreate(BaseModel):
    title: Optional[str] = "Nueva conversación"


class SessionOut(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    created_at: datetime

    model_config = {"from_attributes": True}


class MessageOut(BaseModel):
    id: UUID
    session_id: UUID
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class SendMessageRequest(BaseModel):
    message: str


class SendMessageResponse(BaseModel):
    session_id: UUID
    answer: str
    sources: Optional[List[str]] = None
