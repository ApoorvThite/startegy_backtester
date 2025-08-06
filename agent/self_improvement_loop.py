import json
import os
from agent.strategy_generator import generate_strategy
from agent.evaluator_agent import improve_strategy
from backtest_engine.engine_bt import run_backtest_from_json
from utils.prompts import BASE_STRATEGY_PROMPT

STRATEGY_DIR = "strategies/improved"
STRATEGY_PATH = "strategies/generated/sample_strategy.json"

def save_strategy(strategy, path):
    with open(path, "w") as f:
        json.dump(strategy, f, indent=4)

def log_iteration(i, summary):
    print(f"\n🔁 Iteration {i}")
    print(f"📈 Sharpe Ratio: {summary.get('sharpe')}")
    print(f"📉 Max Drawdown: {summary.get('max_drawdown')}")
    print(f"💰 Total Return: {summary.get('total_return')}")
    print("-" * 40)

def filter_valid_conditions(conditions: list[str]) -> list[str]:
    valid_keywords = ["RSI(", "SMA(", "MACD", "Signal", "Price", "Close", "Upper Bollinger", "Lower Bollinger"]
    return [cond for cond in conditions if any(k.lower() in cond.lower() for k in valid_keywords)]

def self_improvement_loop(n_iterations=5, ticker="AAPL"):
    os.makedirs(STRATEGY_DIR, exist_ok=True)

    # Step 1: Generate strategy
    strategy = generate_strategy(BASE_STRATEGY_PROMPT)

    for i in range(1, n_iterations + 1):
        print(f"\n🚀 Running Iteration {i}...")

        # Step 2: Save current strategy to file
        save_strategy(strategy, STRATEGY_PATH)

        # Step 3: Backtest strategy
        try:
            summary, _ = run_backtest_from_json(STRATEGY_PATH, ticker)
        except Exception as e:
            print(f"❌ Backtest failed on iteration {i}: {e}")
            continue

        # Step 4: Log backtest performance
        log_iteration(i, summary)

        # Step 5: Improve strategy
        strategy = improve_strategy(strategy, summary)

        if not strategy:
            print("⚠️ GPT returned invalid JSON. Skipping iteration.\n")
            continue

        # Step 6: Clean up any vague conditions
        strategy["entry_conditions"] = filter_valid_conditions(strategy.get("entry_conditions", []))
        strategy["exit_conditions"] = filter_valid_conditions(strategy.get("exit_conditions", []))

        # Step 7: Save this iteration’s strategy
        save_path = os.path.join(STRATEGY_DIR, f"strategy_iter_{i}.json")
        save_strategy(strategy, save_path)

if __name__ == "__main__":
    self_improvement_loop()
