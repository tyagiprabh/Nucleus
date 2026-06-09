import os
import uuid
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from agents.router import route
from agents.registry import get_agent, AGENTS

load_dotenv()

app = FastAPI(title="Nucleus API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Component 3: rolling-window memory — last N messages only, never the full dump
MAX_HISTORY = 20

# Session store: session_id → list of Gemini-format messages
sessions: dict[str, list] = {}


class ChatRequest(BaseModel):
    message: str
    session_id: str = ""


class ClearRequest(BaseModel):
    session_id: str


@app.post("/chat")
async def chat(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())

    # Component 3: inject only recent history
    history = sessions.get(session_id, [])[-MAX_HISTORY:]
    history.append({"role": "user", "parts": [{"text": req.message}]})

    # Component 5: Flash router classifies cheaply, specialist executes
    agent_type = route(req.message)
    agent = get_agent(agent_type)

    tools_used = []
    reply = ""

    # Component 6: pass context="" — swap in RAG-retrieved docs here when available
    for event in agent.run(history, context=""):
        if event["type"] == "tool":
            tools_used.append(event["name"])
        elif event["type"] in ("response", "error"):
            reply = event["text"]

    sessions[session_id] = history[-MAX_HISTORY:]

    return {
        "type": "response",
        "text": reply,
        "agent": agent_type,
        "tools_used": tools_used,
        "session_id": session_id,
    }


@app.post("/clear")
async def clear(req: ClearRequest):
    sessions.pop(req.session_id, None)
    return {"ok": True}


@app.get("/health")
async def health():
    return {"status": "ok", "agents": list(AGENTS.keys())}
