title: Form Filling
emoji: 🚀
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
Form Filling OpenEnv

OpenEnv-compatible FastAPI backend — no LLMs, no external APIs, fully deterministic.

📋 Form Filling OpenEnv
OpenEnv-compatible FastAPI backend — no LLMs, no external APIs, fully deterministic.

An environment where an agent extracts structured contact data (name, age, city, phone) from messy, unstructured user text.

🚀 Quick Start
Local
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 7860
Docker
docker build -t form-filling-openenv .
docker run -p 7860:7860 form-filling-openenv
HuggingFace Spaces
Set SDK: Docker in your Space settings. The Dockerfile already exposes port 7860.

🔌 API Reference
GET /
Health check — returns environment metadata.

POST /reset
Start a new episode.

Request

{ "task": "medium", "seed": 42 }
task — easy | medium | hard (default: medium) seed — optional integer for reproducibility

Response

{
  "session_id": "uuid",
  "observation": "hey its prathik rao. im 27. blr based. reach me on 98765 43210.",
  "task": "medium",
  "state_space": { "type": "text", "description": "..." },
  "action_space": { "type": "dict", "fields": ["name","age","city","phone"], "...": "..." },
  "reward_range": [0.0, 1.0]
}
POST /step
Submit the agent's extracted fields.

Request

{
  "session_id": "uuid-from-reset",
  "action": {
    "name":  "Prathik Rao",
    "age":   "27",
    "city":  "Bangalore",
    "phone": "9876543210"
  }
}
Response

{
  "session_id": "uuid",
  "observation": "hey its prathik rao. im 27. blr based. reach me on 98765 43210.",
  "reward": 1.0,
  "done": true,
  "info": {
    "name":  { "predicted": "Prathik Rao", "expected": "Prathik Rao", "reward": 1.0 },
    "age":   { "predicted": "27",          "expected": "27",          "reward": 1.0 },
    "city":  { "predicted": "Bangalore",   "expected": "Bangalore",   "reward": 1.0 },
    "phone": { "predicted": "9876543210",  "expected": "9876543210",  "reward": 1.0 }
  }
}
🏆 Reward Scheme
Outcome	Score
Exact match	1.0
Partial match (alias / substring / age ±1)	0.5
Wrong or missing	0.0
Episode reward = mean(field scores) → range [0.0, 1.0]

📊 Difficulty Levels
Level	Description
easy	Fully labelled, structured input
medium	Abbreviations, casual phrasing, some missing fields
hard	Hinglish, slang, conflicting phones, approximate ages
🗂 Project Structure
├── app.py          ← FastAPI backend (OpenEnv API)
├── env.py          ← FormEnv: reset(), step(), scoring
├── agent.py        ← RuleBasedAgent (regex + keyword matching)
├── inference.py    ← CLI runner: [START][STEP]x5[END]
├── dataset.json    ← 50 labelled examples (easy/medium/hard)
├── openenv.yaml    ← OpenEnv config
├── requirements.txt
└── Dockerfile
ℹ️ Note
"No external APIs or LLMs are used. The environment is fully self-contained and runs offline."
