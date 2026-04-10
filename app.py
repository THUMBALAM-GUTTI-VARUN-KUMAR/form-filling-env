"""
app.py — Form Filling OpenEnv · FastAPI backend
Implements the OpenEnv validator API:  POST /reset  and  POST /step
Compatible with HuggingFace Spaces (port 7860).
"""

import os
import uuid
import random
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from env import FormEnv

# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Form Filling OpenEnv",
    description=(
        "OpenEnv-compatible environment for structured data extraction. "
        "An agent extracts name, age, city, and phone from messy user text."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Session store  (in-memory; one FormEnv per session) ──────────────────────

_sessions: Dict[str, FormEnv] = {}

VALID_TASKS  = ("easy", "medium", "hard")
DEFAULT_TASK = "medium"


def _get_env(session_id: str) -> FormEnv:
    if session_id not in _sessions:
        raise HTTPException(
            status_code=404,
            detail=f"Session '{session_id}' not found. Call /reset first.",
        )
    return _sessions[session_id]


# ── Pydantic models ───────────────────────────────────────────────────────────

class ResetRequest(BaseModel):
    # msg: str = ""
    task: Optional[str] = DEFAULT_TASK 
    seed: Optional[int] = None

model_config = {
    "json_schema_extra": {
        "example": {
            "msg": "",
            "task": "medium",
            "seed": 42
        }
    }
}


class ResetResponse(BaseModel):
    session_id: str
    observation: str
    task: str
    state_space: Dict[str, Any]
    action_space: Dict[str, Any]
    reward_range: list


class ActionModel(BaseModel):
    name:  Optional[str] = "unknown"
    age:   Optional[str] = "unknown"
    city:  Optional[str] = "unknown"
    phone: Optional[str] = "unknown"

    model_config = {
        "json_schema_extra": {
            "example": {
                "name":  "Priya Nair",
                "age":   "28",
                "city":  "Mumbai",
                "phone": "9876543210",
            }
        }
    }


class StepRequest(BaseModel):
    session_id: str
    action: ActionModel

    model_config = {
        "json_schema_extra": {
            "example": {
                "session_id": "abc-123",
                "action": {
                    "name":  "Priya Nair",
                    "age":   "28",
                    "city":  "Mumbai",
                    "phone": "9876543210",
                },
            }
        }
    }


class FieldInfo(BaseModel):
    predicted: str
    expected:  str
    reward:    float


class StepResponse(BaseModel):
    session_id:  str
    observation: str
    reward:      float
    done:        bool
    info:        Dict[str, FieldInfo]


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "name": "form_filling_openenv",
        "type": "environment",
        "tasks": [
            {"id": "easy", "grader": "reward_based"},
            {"id": "medium", "grader": "reward_based"},
            {"id": "hard", "grader": "reward_based"}
        ]
    }


@app.get("/health", summary="Liveness probe")
def health():
    return {"status": "ok"}


@app.post("/reset", response_model=ResetResponse, summary="Start a new episode")
def reset(body: ResetRequest = ResetRequest()):
    """
    Start a new episode.
    - **task**: `easy` | `medium` | `hard`  (default: `medium`)
    - **seed**: optional integer for reproducible sampling
    Returns a `session_id` and the raw messy `observation` text the agent must parse.
    """
    task = (body.task or DEFAULT_TASK).lower()
    if task not in VALID_TASKS:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid task '{task}'. Valid options: {list(VALID_TASKS)}",
        )

    if body.seed is not None:
        random.seed(body.seed)

    env         = FormEnv(difficulty=task)
    observation = env.reset()["observation"]
    session_id  = str(uuid.uuid4())
    _sessions[session_id] = env

    return ResetResponse(
        session_id   = session_id,
        observation  = observation,
        task         = task,
        state_space  = env.state_space,
        action_space = env.action_space,
        reward_range = list(env.reward_range),
    )


@app.post("/step", response_model=StepResponse, summary="Submit an action")
def step(body: StepRequest):
    """
    Submit the agent's extracted fields for the current episode.
    - **session_id**: returned by `/reset`
    - **action**: `{name, age, city, phone}` — use `"unknown"` for missing fields
    Returns `reward` (0.0 – 1.0), `done` (always `true` for single-turn), and
    a per-field breakdown in `info`.
    """
    env = _get_env(body.session_id)

    action_dict = {
        "name":  body.action.name  or "unknown",
        "age":   body.action.age   or "unknown",
        "city":  body.action.city  or "unknown",
        "phone": body.action.phone or "unknown",
    }

    try:
        observation, reward, done, info = env.step(action_dict)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # Free the session once the episode is complete
    if done:
        _sessions.pop(body.session_id, None)

    return StepResponse(
        session_id  = body.session_id,
        observation = observation,
        reward      = reward,
        done        = done,
        info        = {
            field: FieldInfo(
                predicted = str(data["predicted"]),
                expected  = str(data["expected"]),
                reward    = float(data["reward"]),
            )
            for field, data in info.items()
        },
    )


# ── HuggingFace Spaces / local entry point ────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
