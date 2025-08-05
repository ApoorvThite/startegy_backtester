import openai
import json
from datetime import datetime
import re
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def clean_strategy_fields(strategy):
    """Ensure all conditions are in parseable format like 'RSI(14) < 30'."""

    def parse_condition(cond):
        # Convert verbose natural language to valid expressions
        cond = cond.lower()

        # RSI
        if "rsi" in cond and "crosses above" in cond:
            match = re.search(r"rsi.*?(\d+)", cond)
            period = match.group(1) if match else "14"
            threshold = re.search(r"above\s+(\d+)", cond)
            value = threshold.group(1) if threshold else "70"
            return f"RSI({period}) > {value}"

        elif "rsi" in cond and "crosses below" in cond:
            match = re.search(r"rsi.*?(\d+)", cond)
            period = match.group(1) if match else "14"
            threshold = re.search(r"below\s+(\d+)", cond)
            value = threshold.group(1) if threshold else "30"
            return f"RSI({period}) < {value}"

        # MACD (support basic parsing, not implemented yet)
        if "macd line crosses above" in cond:
            return "MACD > Signal"
        elif "macd line crosses below" in cond:
            return "MACD < Signal"

        # Default: return as-is
        return cond.strip()

    strategy["entry_conditions"] = [parse_condition(c) for c in strategy.get("entry_conditions", [])]
    strategy["exit_conditions"] = [parse_condition(c) for c in strategy.get("exit_conditions", [])]
    return strategy


def generate_strategy(prompt: str, model="gpt-4", temperature=0.7):
    system_prompt = (
        "You are an expert quantitative trading assistant. "
        "Generate trading strategies based on technical indicators. "
        "Output should be valid JSON with the following fields: "
        "strategy_name, description, entry_conditions (list of conditions like 'RSI(14) < 30'), "
        "exit_conditions (same format), stop_loss, take_profit, timeframe."
    )

    user_prompt = f"Generate a trading strategy. Focus: {prompt}"

    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=temperature
    )

    content = response['choices'][0]['message']['content']

    try:
        strategy = json.loads(content)
        strategy['generated_at'] = str(datetime.now())
        strategy = clean_strategy_fields(strategy)
        return strategy

    except json.JSONDecodeError:
        print("⚠️ GPT returned malformed JSON:")
        print(content)
        return None
