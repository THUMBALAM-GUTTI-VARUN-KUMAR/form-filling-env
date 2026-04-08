"""
env.py - FormFilling OpenEnv Environment
"""

import json
import random
import os


class FormEnv:
    """
    OpenEnv-style environment for structured data extraction from messy text.

    State  : raw messy input string
    Action : dict with keys {name, age, city, phone}
    Reward : 0.0–1.0  (normalised sum of per-field scores / num_fields)
    Done   : True after each step (single-turn episode)
    """

    FIELDS = ["name", "age", "city", "phone"]

    def __init__(self, dataset_path: str = "dataset.json", difficulty: str = "medium"):
        if difficulty not in ("easy", "medium", "hard"):
            raise ValueError("difficulty must be 'easy', 'medium', or 'hard'")

        dataset_path = os.path.join(os.path.dirname(__file__), dataset_path)
        with open(dataset_path, "r", encoding="utf-8") as f:
            all_data = json.load(f)

        self.examples = all_data[difficulty]
        self.difficulty = difficulty
        self._current = None
        self._done = True

    # ------------------------------------------------------------------
    def reset(self) -> str:
        """Pick a random example and return the raw input text."""
        self._current = random.choice(self.examples)
        self._done = False
        return self._current["input"]

    # ------------------------------------------------------------------
    def step(self, action: dict):
        """
        Compare the agent's predicted fields against the expected target.

        Parameters
        ----------
        action : dict  {name, age, city, phone}  (values may be "unknown")

        Returns
        -------
        state  : str   — same input (episode is single-turn)
        reward : float — total reward (0–4)
        done   : bool  — always True after one step
        info   : dict  — per-field breakdown
        """
        if self._done:
            raise RuntimeError("Call reset() before step().")

        target = self._current["target"]
        info = {}
        total_reward = 0.0

        for field in self.FIELDS:
            predicted = str(action.get(field, "unknown")).strip().lower()
            expected_raw = target.get(field)

            if expected_raw is None:
                # Field genuinely missing in target — correct if agent says unknown
                expected = "unknown"
            else:
                expected = str(expected_raw).strip().lower()

            reward = self._score_field(field, predicted, expected)
            total_reward += reward
            info[field] = {
                "predicted": action.get(field, "unknown"),
                "expected": target.get(field) or "unknown",
                "reward": reward,
            }

        self._done = True
        state = self._current["input"]
        normalised = round(total_reward / len(self.FIELDS), 2)
        return state, normalised, True, info

    # ------------------------------------------------------------------
    def _score_field(self, field: str, predicted: str, expected: str) -> float:
        """Return 1.0, 0.5, or 0.0 for a single field."""
        if predicted == expected:
            return 1.0

        # Partial match: predicted is contained in expected or vice-versa
        if predicted != "unknown" and expected != "unknown":
            if predicted in expected or expected in predicted:
                return 0.5

            # Phone: strip spaces/dashes and compare
            if field == "phone":
                p_clean = predicted.replace(" ", "").replace("-", "")
                e_clean = expected.replace(" ", "").replace("-", "")
                if p_clean == e_clean:
                    return 1.0
                if p_clean in e_clean or e_clean in p_clean:
                    return 0.5

            # Age: accept ±1 year
            if field == "age":
                try:
                    if abs(int(predicted) - int(expected)) <= 1:
                        return 0.5
                except ValueError:
                    pass

            # City abbreviation aliases
            if field == "city":
                aliases = {
                    "blr": "bangalore", "bng": "bangalore",
                    "mum": "mumbai", "bom": "mumbai",
                    "hyd": "hyderabad",
                    "del": "delhi", "ndl": "delhi",
                    "che": "chennai", "maa": "chennai", "madras": "chennai",
                    "kol": "kolkata", "cal": "kolkata", "kalkatta": "kolkata",
                    "pune": "pune",
                    "lko": "lucknow",
                    "ahm": "ahmedabad",
                    "jpr": "jaipur",
                    "ngp": "nagpur",
                    "prayagraj": "allahabad",
                }
                p_norm = aliases.get(predicted, predicted)
                e_norm = aliases.get(expected, expected)
                if p_norm == e_norm:
                    return 1.0
                if p_norm in e_norm or e_norm in p_norm:
                    return 0.5

        return 0.0

    # ------------------------------------------------------------------
    @property
    def state_space(self) -> dict:
        return {"type": "text", "description": "Free-form messy user input string"}

    @property
    def action_space(self) -> dict:
        return {
            "type": "dict",
            "fields": self.FIELDS,
            "description": "Extracted structured fields; use 'unknown' if missing",
        }

    @property
    def reward_range(self) -> tuple:
        return (0.0, 1.0)
