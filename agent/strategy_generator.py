import openai
import json
import os
from datetime import datetime
from utils.prompts import BASE_STRATEGY_PROMPT

def generate_strategy(prompt: str = BASE_STRATEGY_PROMPT) -> dict:
    openai.api_key = os.getenv("OPENAI_API_KEY")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )

        content = response["choices"][0]["message"]["content"]

        # Try to clean up the JSON if GPT adds formatting by mistake
        content = content.strip()
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()

        strategy = json.loads(content)

        # Add timestamp if not present
        if "generated_at" not in strategy:
            strategy["generated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return strategy

    except json.JSONDecodeError as e:
        print("❌ GPT returned invalid JSON. Error:", e)
        return None

    except Exception as e:
        print("❌ Error generating strategy:", e)
        return None

