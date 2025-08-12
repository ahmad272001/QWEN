import os
import uuid
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Initialize FastAPI app
app = FastAPI(
    title="Signize AI Chatbot",
    description="RAG-powered customer support for custom signage",
    version="1.0.0"
)

# CORS setup (allow frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(BASE_DIR, "pdfs")
CHROMA_DIR = os.path.join(BASE_DIR, "chromadb")
os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(CHROMA_DIR, exist_ok=True)

# --- Import local modules (after path setup) ---
try:
    from database import save_message, get_chat_history
    from rag_engine import add_pdfs_from_dir, get_rag_chain
    from hubspot_sync import push_session_to_hubspot
    from system_prompt import SYSTEM_PROMPT
except Exception as e:
    print(f"❌ Import error: {e}")
    raise

# --- Models ---
class MessageRequest(BaseModel):
    session_id: Optional[str] = None
    message: str

# --- Health Check ---
@app.get("/")
def health():
    return {
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "pdf_dir": PDF_DIR,
        "chroma_dir": CHROMA_DIR,
        "files_in_pdf_dir": os.listdir(PDF_DIR) if os.path.exists(PDF_DIR) else [],
        "env": "production"
    }

# --- Startup Event: Load PDF into ChromaDB ---
@app.on_event("startup")
def load_knowledge_base():
    print("🚀 Starting Signize AI Chatbot...")
    print(f"📄 PDF Directory: {PDF_DIR}")
    print(f"🧠 ChromaDB Directory: {CHROMA_DIR}")

    # Copy TestPdf.pdf to pdfs/ if not exists
    source_pdf = os.path.join(BASE_DIR, "..", "TestPdf.pdf")
    if not os.path.exists(source_pdf):
        source_pdf = os.path.join(BASE_DIR, "TestPdf.pdf")

    if not os.path.exists(source_pdf):
        print("❌ TestPdf.pdf not found in root or backend!")
    else:
        target_pdf = os.path.join(PDF_DIR, "signage_guide.pdf")
        if not os.path.exists(target_pdf):
            try:
                import shutil
                shutil.copy(source_pdf, target_pdf)
                print(f"📎 Copied TestPdf.pdf to {target_pdf}")
            except Exception as e:
                print(f"❌ Failed to copy PDF: {e}")

    # Ingest PDFs into ChromaDB
    try:
        add_pdfs_from_dir(PDF_DIR)
        print("✅ Knowledge base loaded into ChromaDB!")
    except Exception as e:
        print(f"❌ Failed to ingest PDF: {e}")

# --- Chat Endpoint ---
@app.post("/chat")
async def chat(req: MessageRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    # Generate or use session ID
    session_id = req.session_id or str(uuid.uuid4())

    # Save user message
    save_message(session_id, "user", req.message)

    # Get chat history
    history = get_chat_history(session_id)
    chat_pairs = [(m["role"], m["content"]) for m in history if m["role"] in ["user", "assistant"]]

    # Inject current date into system prompt
    today = datetime.now().strftime("%B %d, %Y")
    dynamic_prompt = SYSTEM_PROMPT.replace("{{date}}", today)

    try:
        # Get RAG chain with updated prompt
        chain = get_rag_chain(dynamic_prompt)

        # Invoke chain
        result = chain.invoke({
            "question": req.message,
            "chat_history": chat_pairs
        })

        ai_response = result["answer"].strip()

        # Save assistant message
        save_message(session_id, "assistant", ai_response)

        # Sync to HubSpot in background
        from threading import Thread
        Thread(target=push_session_to_hubspot, args=(session_id, get_chat_history(session_id)), daemon=True).start()

        return {
            "response": ai_response,
            "session_id": session_id
        }

    except Exception as e:
        error_msg = "I'm having trouble processing your request. Please try again later."
        save_message(session_id, "assistant", error_msg)
        print(f"❌ LLM Error: {e}")
        return {
            "response": error_msg,
            "session_id": session_id
        }

# --- Optional: Get chat history ---
@app.get("/history/{session_id}")
def get_history(session_id: str):
    try:
        history = get_chat_history(session_id)
        return {"history": history}
    except Exception as e:
        print(f"❌ History fetch error: {e}")
        return {"history": [], "error": "Could not load history"}
