import os
import json
import uuid
import anthropic
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from tools.registry import TOOLS, execute_tool

load_dotenv()

app = FastAPI(title="Nucleus API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SYSTEM = """You are Nucleus — an HR Intelligence assistant for Iris Galerie, a luxury jewelry gallery
with stores across Europe (Spain, Italy, Netherlands, Poland, France) and Asia (Singapore).

Systems at Iris Galerie: CEGID Y2 (retail POS), Odoo 19 (ERP), Google Workspace, Freshservice (helpdesk), NX Witness (store cameras).

Use the available tools whenever they add specific value (checklists, compliance data, candidate search).
For job descriptions, interview questions, or translations — answer directly without a tool.
Be concise and actionable. The human makes all final decisions.

Current date: June 2026."""

# In-memory session store: session_id -> list of message dicts
sessions: dict[str, list] = {}


def serialize_block(block) -> dict:
    if block.type == "text":
        return {"type": "text", "text": block.text}
    if block.type == "tool_use":
        return {"type": "tool_use", "id": block.id, "name": block.name, "input": block.input}
    return {"type": block.type}


class ChatRequest(BaseModel):
    message: str
    session_id: str = ""


class ClearRequest(BaseModel):
    session_id: str


@app.post("/chat")
async def chat(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())
    history = sessions.get(session_id, [])
    history.append({"role": "user", "content": req.message})

    async def stream():
        client = anthropic.Anthropic()
        current_history = list(history)

        while True:
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=4096,
                system=SYSTEM,
                tools=TOOLS,
                messages=current_history,
            )

            if response.stop_reason == "end_turn":
                reply = next((b.text for b in response.content if hasattr(b, "text")), "")
                current_history.append({
                    "role": "assistant",
                    "content": [serialize_block(b) for b in response.content],
                })
                sessions[session_id] = current_history
                yield f"data: {json.dumps({'type': 'response', 'text': reply})}\n\n"
                break

            if response.stop_reason == "tool_use":
                current_history.append({
                    "role": "assistant",
                    "content": [serialize_block(b) for b in response.content],
                })

                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        yield f"data: {json.dumps({'type': 'tool', 'name': block.name})}\n\n"
                        result = execute_tool(block.name, block.input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        })

                current_history.append({"role": "user", "content": tool_results})

    return StreamingResponse(stream(), media_type="text/event-stream")


@app.post("/clear")
async def clear(req: ClearRequest):
    sessions.pop(req.session_id, None)
    return {"ok": True}


@app.get("/health")
async def health():
    return {"status": "ok", "tools": len(TOOLS)}
