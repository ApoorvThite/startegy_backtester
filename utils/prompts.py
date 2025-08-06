import json

def get_improvement_prompt(strategy: dict, summary: dict) -> str:
    return f"""
You are a trading strategy expert AI.

Below is a trading strategy and its backtest performance summary.

Your task:
- Improve the strategy to maximize the Sharpe ratio
- Reduce the drawdown
- Keep the core logic and style of the original strategy intact

⚠️ Only return a clean JSON object using the exact format below.
⚠️ DO NOT include explanations, markdown, or code blocks.

Strategy:
{json.dumps(strategy, indent=2)}

Backtest Summary:
{json.dumps(summary, indent=2)}

Output format:
{{
  "strategy_name": "...",
  "description": "...",
  "entry_conditions": ["...", "..."],
  "exit_conditions": ["...", "..."],
  "stop_loss": 0.02,
  "take_profit": 0.05,
  "timeframe": "15m",
  "generated_at": "YYYY-MM-DD HH:MM:SS"
}}
"""

BASE_STRATEGY_PROMPT = """
You are a trading strategy generator. Create a JSON strategy object for a short-term momentum strategy using RSI, MACD, and Bollinger Bands.

Strictly follow this structure:

{
  "strategy_name": "...",
  "description": "...",
  "entry_conditions": [
    "RSI(14) > 70",
    "MACD > Signal",
    "Close > Upper Bollinger Band"
  ],
  "exit_conditions": [
    "RSI(14) < 30",
    "MACD < Signal",
    "Close < Lower Bollinger Band"
  ],
  "stop_loss": 0.02,
  "take_profit": 0.05,
  "timeframe": "15m",
  "generated_at": "YYYY-MM-DD HH:MM:SS"
}

❗ Only use these formats:
- RSI(x) > n or RSI(x) < n
- MACD > Signal or MACD < Signal
- Close > Upper Bollinger Band
- Close < Lower Bollinger Band
- SMA(x) crosses above SMA(y)
❌ Do not use words like "indicating", "confirming", "trailing stop", or "ADX"
"""

