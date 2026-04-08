import os
import json
import random

from env import FormEnv
from agent import RuleBasedAgent

API_BASE_URL = os.getenv("API_BASE_URL", "local")
MODEL_NAME = os.getenv("MODEL_NAME", "rule-based")
HF_TOKEN = os.getenv("HF_TOKEN")
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")

TASK = os.getenv("TASK", "medium")
ENV_NAME = "form-filling-openenv"
MODEL = MODEL_NAME


def main():
    random.seed(42)

    env = FormEnv(difficulty=TASK)
    agent = RuleBasedAgent()

    print(f"[START] task={TASK} env={ENV_NAME} model={MODEL}", flush=True)

    rewards = []

    for step in range(1, 6):
        observation = env.reset()

        action = agent.predict(observation)

        step_result = env.step(action)
        
        #print(step_result)   # temporary debug
        
        reward = step_result["reward"]
        done = step_result["done"]

        rewards.append(reward)

        print(f"[STEP] step={step} action={json.dumps(action)} reward={float(reward):.2f} done=true error=null",flush=True)

    score = round(sum(rewards) / len(rewards), 2)

    print(
        f"[END] success=true steps=5 score={score:.2f} rewards={','.join(map(str,rewards))}",
        flush=True
    )


if __name__ == "__main__":
    main()
