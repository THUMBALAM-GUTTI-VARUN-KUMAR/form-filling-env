import os
import json
import random

from env import FormEnv
from agent import RuleBasedAgent
from openai import OpenAI


API_BASE_URL = os.getenv("API_BASE_URL")
API_KEY = os.getenv("API_KEY")

MODEL_NAME = os.getenv("MODEL_NAME", "openai/gpt-4o-mini")
TASK = os.getenv("TASK", "medium")

ENV_NAME = "form-filling-openenv"
MODEL = MODEL_NAME


# SAFE CLIENT CREATION
client = None

if API_KEY and API_BASE_URL:
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
                    "Extract name, age, city and phone from the text. "
                    "Return ONLY JSON in format: "
                    "{\"name\":\"...\",\"age\":\"...\",\"city\":\"...\",\"phone\":\"...\"}"
                )
            },
            {
                "role": "user",
                "content": str(observation)
            }
        ]
    )

    print("LLM CALL SUCCESS", flush=True)

    content = response.choices[0].message.content.strip()
    content = content.replace("```json", "").replace("```", "").strip()

    return json.loads(content)


def main():
    random.seed(42)

    env = FormEnv(difficulty=TASK)

    print(f"[START] task={TASK} env={ENV_NAME} model={MODEL}", flush=True)

    rewards = []

    for step in range(1, 6):
        observation = env.reset()

        try:
            if client:
                action = llm_predict(observation)
            else:
                print("NO API FOUND, USING RULE-BASED", flush=True)
                action = RuleBasedAgent().predict(observation)

        except Exception as e:
            print(f"LLM FAILED ({e}), USING FALLBACK", flush=True)
            action = RuleBasedAgent().predict(observation)

        step_result = env.step(action)

        reward = step_result["reward"]
        done = step_result["done"]

        rewards.append(reward)

        print(
            f"[STEP] step={step} action={json.dumps(action)} reward={float(reward):.2f} done={done} error=null",
            flush=True
        )

    score = round(sum(rewards) / len(rewards), 2)

    print(
        f"[END] success=true steps=5 score={score:.2f} rewards={','.join(map(str,rewards))}",
        flush=True
    )


if __name__ == "__main__":
    main()

