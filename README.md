---
title: Form Filling OpenEnv
emoji: 🚀
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
---

# 📋 Form Filling OpenEnv

OpenEnv-compatible FastAPI backend for structured information extraction using **LLM + Rule-Based fallback**.

An intelligent environment where an agent extracts structured contact data (**name, age, city, phone**) from messy, unstructured user text.

Supports:

- ✅ LLM-powered extraction via hackathon LiteLLM proxy  
- ✅ Rule-based fallback if LLM fails/unavailable  
- ✅ OpenEnv-compatible FastAPI backend  
- ✅ Docker / HuggingFace deployment ready  

---

# 🚀 Quick Start

## Local

```bash
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 7860
```

## Docker

```bash
docker build -t form-filling-openenv .
docker run -p 7860:7860 form-filling-openenv
```

## HuggingFace Spaces

Set SDK: **Docker** in Space settings.

Dockerfile already exposes **port 7860**.

---

# 🔌 API Reference

## GET /

Health check endpoint.

Returns environment metadata.

---

## POST /reset

Start new episode.

### Request

```json
{
  "task": "medium",
  "seed": 42
}
```

### Parameters

- `task` → easy / medium / hard  
- `seed` → optional integer  

---

### Response

```json
{
  "session_id": "uuid",
  "observation": "hey its prathik rao. im 27. blr based. reach me on 98765 43210.",
  "task": "medium"
}
```

---

## POST /step

Submit extracted fields.

### Request

```json
{
  "session_id": "uuid",
  "action": {
    "name": "Prathik Rao",
    "age": "27",
    "city": "Bangalore",
    "phone": "9876543210"
  }
}
```

---

### Response

```json
{
  "reward": 1.0,
  "done": true
}
```

---

# 🏆 Reward Scheme

| Outcome | Score |
|--------|------|
| Exact Match | 1.0 |
| Partial Match | 0.5 |
| Wrong/Missing | 0.0 |

Final Reward:

```text
Average(field_scores)
```

Range:

```text
0.0 → 1.0
```

---

# 📊 Difficulty Levels

| Level | Description |
|-------|------------|
| Easy | Structured labelled inputs |
| Medium | Abbreviations + casual phrasing |
| Hard | Hinglish/slang/noisy/adversarial |

---

# 🗂 Project Structure

```text
app.py            FastAPI backend
server/app.py     Deployment server entry
env.py            OpenEnv environment logic
agent.py          RuleBased fallback agent
inference.py      Main evaluation runner
dataset.json      Training/evaluation examples
openenv.yaml      OpenEnv config
requirements.txt  Dependencies
Dockerfile        Deployment container
```

---

# ⚙️ Architecture

This project uses:

### Primary:
- LiteLLM/OpenAI-compatible API proxy for intelligent extraction

### Fallback:
- Regex/Rule-based parsing if LLM unavailable

This ensures:

- Robust performance  
- Proxy validation compatibility  
- Graceful failure handling  

---

# ℹ️ Note

Built for **Meta x PyTorch Hackathon OpenEnv Challenge**.

Optimized for:

- Multi-mode deployment  
- HuggingFace Spaces  
- Hackathon validator compatibility
