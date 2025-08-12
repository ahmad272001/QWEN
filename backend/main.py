from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
from datetime import datetime
import os
import shutil
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Import local modules ---
from database import save_message, get_chat_history
from rag_engine import add_pdfs_from_dir, get_rag_chain
from hubspot_sync import push_session_to_hubspot

# --- Paths ---
UPLOAD_DIR = "./uploads"
PDF_DIR = "./pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)

# Preload your PDF
if not os.listdir(PDF_DIR):
    shutil.copy("../TestPdf.pdf", f"{PDF_DIR}/signage_guide.pdf")
    add_pdfs_from_dir(PDF_DIR)  # Ingest on startup

# --- Models ---
class MessageRequest(BaseModel):
    session_id: Optional[str] = None
    message: str

@app.post("/chat")
async def chat(req: MessageRequest):
    session_id = req.session_id or str(uuid.uuid4())
    user_message = req.message

    # Save user message
    save_message(session_id, "user", user_message)

    # Inject current date into system prompt
    from system_prompt import SYSTEM_PROMPT
    dynamic_prompt = SYSTEM_PROMPT.replace("{{date}}", datetime.now().strftime("%B %d, %Y"))

    # Get RAG chain with updated prompt
    chain = get_rag_chain(dynamic_prompt)
    history = get_chat_history(session_id)
    chat_pairs = [(h["role"], h["content"]) for h in history if h["role"] in ["human", "user", "assistant"]]

    try:
        result = chain.invoke({
            "question": user_message,
            "chat_history": chat_pairs
        })
        ai_response = result["answer"]
    except Exception as e:
        ai_response = "I'm having trouble processing your request. Please try again."

    # Save AI response
    save_message(session_id, "assistant", ai_response)

    # Async sync to HubSpot
    from threading import Thread
    Thread(target=push_session_to_hubspot, args=(session_id, get_chat_history(session_id)), daemon=True).start()

    return {
        "response": ai_response,
        "session_id": session_id
    }

@app.get("/history/{session_id}")
def get_history(session_id: str):
    return {"history": get_chat_history(session_id)}

@app.on_event("startup")
def startup_event():
    add_pdfs_from_dir(PDF_DIR)