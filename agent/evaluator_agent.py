from utils.prompts import get_improvement_prompt
from utils.gpt_utils import call_gpt
import json

def improve_strategy(strategy: dict, backtest_summary: dict) -> dict:
    prompt = get_improvement_prompt(strategy, backtest_summary)
    improved_strategy_json = call_gpt(prompt)
    try:
        return json.loads(improved_strategy_json)
    except json.JSONDecodeError:
        print("⚠️ GPT returned invalid JSON. Keeping previous strategy.")
        return strategy
