# Nucleus — Iris Galerie HR Intelligence

An AI-powered HR assistant for Iris Galerie, built on Claude (Anthropic). Nucleus routes HR requests to specialist agents and visualises the agent network as an interactive space UI.

## What it does

Type a request in plain language — Nucleus decides which agent to activate and returns a structured, Iris Galerie-specific answer.

| Agent | What it handles |
|-------|----------------|
| Candidate Research | Searches LinkedIn, Indeed & Glassdoor for candidates |
| Onboarding | Generates IT setup checklists + day 1 schedules per country |
| Offboarding | Access revocation order + country-specific legal exit steps |
| Compliance | Employment law for Spain, Italy, Netherlands, Poland, Singapore, France |

More agents can be added in `backend/tools/` — one file, one function, one schema entry.

## Try these prompts

- `Onboard Sophie Martin, Store Manager, Madrid, starting June 16`
- `Write a job description for a Sales Associate in Amsterdam`
- `What are the sick leave rules in Poland?`
- `Offboard Jean Dupont, Sales Associate, Netherlands, last day June 30`
- `Find candidates for a Store Manager in Madrid`
- `Generate interview questions for a Store Manager`

## Tech stack

- **Frontend** — React + Vite, canvas-based space visualization, hosted on Vercel
- **Backend** — FastAPI + Anthropic SDK (Claude Sonnet), hosted on Railway
- **AI** — Claude `claude-sonnet-4-6` with tool use (agentic loop)

## Local development

**Backend**
```bash
cd backend
cp .env.example .env        # add ANTHROPIC_API_KEY
pip install -r requirements.txt
uvicorn api:app --reload --port 8000
```

**Frontend**
```bash
cd frontend
npm install
npm run dev                  # opens http://localhost:5173
```

## Deployment

| Service | Directory | Config file |
|---------|-----------|-------------|
| Railway (backend) | `backend/` | `railway.toml` |
| Vercel (frontend) | `frontend/` | `vercel.json` |

Set `VITE_BACKEND_URL` in Vercel to your Railway backend URL.

## Adding a new agent

1. Create `backend/tools/my_tool.py` with a function that returns a JSON string
2. Add it to `TOOL_FUNCTIONS` and `TOOLS` in `backend/tools/registry.py`
3. Add a planet entry in `frontend/src/components/SpaceNetwork.jsx`

Done — Nucleus picks it up automatically.

## Project structure

```
nucleus/
├── backend/
│   ├── api.py                  # FastAPI — /chat (SSE), /clear, /health
│   ├── railway.toml            # Railway deploy config
│   ├── requirements.txt
│   └── tools/
│       ├── registry.py         # Tool schemas + dispatcher
│       ├── candidate_research.py
│       ├── onboarding.py
│       ├── offboarding.py
│       └── compliance.py
└── frontend/
    ├── vercel.json             # Vercel deploy config
    ├── vite.config.js
    └── src/
        ├── App.jsx
        └── components/
            ├── SpaceNetwork.jsx  # Canvas space visualization
            └── ChatPanel.jsx     # Chat interface + SSE streaming
```

---

Built by Prabhat Tyagi — Iris Galerie IT · June 2026
