import os
import json
import random

from env import FormEnv
from agent import RuleBasedAgent

TASK     = os.environ.get("TASK", "medium")
ENV_NAME = "form-filling-openenv"
MODEL    = "rule-based"

def main():
    random.seed(42)
    env   = FormEnv(difficulty=TASK)
    agent = RuleBasedAgent()

    print(f"[START] task={TASK} env={ENV_NAME} model={MODEL}", flush=True)

    rewards = []
    for step in range(1, 6):
        observation        = env.reset()
        action             = agent.predict(observation)
        _, reward, done, _ = env.step(action)
        rewards.append(reward)

        action_str = json.dumps(action, separators=(",", ":"), ensure_ascii=False)
        done_str   = "true" if done else "false"
        print(f"[STEP] step={step} action={action_str} reward={reward:.2f} done={done_str} error=null", flush=True)

    score       = round(sum(rewards) / len(rewards), 2)
    success_str = "true" if score >= 0.5 else "false"
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={success_str} steps=5 score={score:.2f} rewards={rewards_str}", flush=True)

if __name__ == "__main__":
    main()
