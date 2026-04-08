import os
import json
import random

from env import FormEnv
from openai import OpenAI


API_BASE_URL = os.environ["API_BASE_URL"]
API_KEY = os.environ["API_KEY"]

MODEL_NAME = os.getenv("MODEL_NAME", "openai/gpt-4o-mini")
TASK = os.getenv("TASK", "medium")

ENV_NAME = "form-filling-openenv"
MODEL = MODEL_NAME


client = OpenAI(
    api_key=API_KEY,
    base_url=API_BASE_URL
)


def llm_predict(observation):
    print("LLM CALL STARTING", flush=True)
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "Extract name, age, city, and phone from the given text. "
                    "Return ONLY valid JSON in this format: "
                    "{\"name\":\"...\",\"age\":0,\"city\":\"...\",\"phone\":\"...\"}"
                )
            },
            {
                "role": "user",
                "content": str(observation)
            }
        ]
    )
    print("LLM CALL FINISHED", flush=True)
    return json.loads(response.choices[0].message.content)


def main():
    random.seed(42)

    env = FormEnv(difficulty=TASK)

    print(f"[START] task={TASK} env={ENV_NAME} model={MODEL}", flush=True)

    rewards = []

    for step in range(1, 6):
        observation = env.reset()

        action = llm_predict(observation)

        step_result = env.step(action)

        reward = step_result["reward"]

        rewards.append(reward)

        print(
            f"[STEP] step={step} action={json.dumps(action)} reward={float(reward):.2f} done=true error=null",
            flush=True
        )

    score = round(sum(rewards) / len(rewards), 2)

    print(
        f"[END] success=true steps=5 score={score:.2f} rewards={','.join(map(str,rewards))}",
        flush=True
    )


if __name__ == "__main__":
    main()
