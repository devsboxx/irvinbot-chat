from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat_router, thesis_router
from app.core.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="irvinbot-chat", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router.router, prefix="/chat", tags=["chat"])
app.include_router(thesis_router.router, prefix="/thesis", tags=["thesis"])


@app.get("/health")
def health():
    return {"status": "ok", "service": "chat"}
