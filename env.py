"""
env.py - FormFilling OpenEnv Environment
"""

import json
import random
import os


class FormEnv:

    FIELDS = ["name", "age", "city", "phone"]

    TASK_MAP = {
        "basic_extraction": "easy",
        "noisy_extraction": "medium",
        "adversarial_extraction": "hard"
    }

    def __init__(self, dataset_path="dataset.json", task="noisy_extraction"):

        if task not in self.TASK_MAP:
            raise ValueError(
                f"task must be one of {list(self.TASK_MAP.keys())}"
            )

        dataset_path = os.path.join(os.path.dirname(__file__), dataset_path)

        with open(dataset_path, "r", encoding="utf-8") as f:
            all_data = json.load(f)

        difficulty = self.TASK_MAP[task]

        self.examples = all_data[difficulty]
        self.task = task
        self._current = None
        self._done = True

    def reset(self):

        self._current = random.choice(self.examples)
        self._done = False

        return {
            "observation": self._current["input"]
        }

    def step(self, action: dict):

        if self._done:
            raise RuntimeError("Call reset() before step().")

        target = self._current["target"]

        info = {}
        total_reward = 0.0

        for field in self.FIELDS:

            predicted = str(action.get(field, "unknown")).strip().lower()

            expected_raw = target.get(field)

            expected = (
                "unknown"
                if expected_raw is None
                else str(expected_raw).strip().lower()
            )

            reward = self._score_field(field, predicted, expected)

            total_reward += reward

            info[field] = {
                "predicted": action.get(field, "unknown"),
                "expected": target.get(field) or "unknown",
                "reward": reward,
            }

        self._done = True

        return {
            "observation": self._current["input"],
            "reward": round(total_reward / len(self.FIELDS), 2),
            "done": True,
            "info": info
        }

    def _score_field(self, field, predicted, expected):

        if predicted == expected:
            return 1.0

        if predicted != "unknown" and expected != "unknown":

            if predicted in expected or expected in predicted:
                return 0.5

            if field == "phone":

                p = predicted.replace(" ", "").replace("-", "")
                e = expected.replace(" ", "").replace("-", "")

                if p == e:
                    return 1.0

                if p in e or e in p:
                    return 0.5

            if field == "age":

                try:
                    if abs(int(predicted) - int(expected)) <= 1:
                        return 0.5
                except:
                    pass

            if field == "city":

                aliases = {
                    "blr": "bangalore",
                    "hyd": "hyderabad",
                    "mum": "mumbai",
                    "del": "delhi"
                }

                p_norm = aliases.get(predicted, predicted)
                e_norm = aliases.get(expected, expected)

                if p_norm == e_norm:
                    return 1.0

                if p_norm in e_norm or e_norm in p_norm:
                    return 0.5

        return 0.0

    @property
    def state_space(self):

        return {
            "type": "text"
        }

    @property
    def action_space(self):

        return {
            "type": "dict",
            "fields": self.FIELDS
        }

    @property
    def reward_range(self):

        return (0.0, 1.0)
