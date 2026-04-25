from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from app.models.chat import Message
from typing import List
import uuid


def load_history(db: Session, session_id: uuid.UUID) -> List[BaseMessage]:
    messages = (
        db.query(Message)
        .filter(Message.session_id == session_id)
        .order_by(Message.created_at)
        .all()
    )
    history: List[BaseMessage] = []
    for msg in messages:
        if msg.role == "user":
            history.append(HumanMessage(content=msg.content))
        else:
            history.append(AIMessage(content=msg.content))
    return history
