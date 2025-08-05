from agent.strategy_generator import generate_strategy
import json

prompt = "Short-term momentum strategy for volatile tech stocks"
strategy = generate_strategy(prompt)

if strategy:
    with open("strategies/generated/sample_strategy.json", "w") as f:
        json.dump(strategy, f, indent=4)
        print("✅ Strategy saved to strategies/generated/sample_strategy.json")
else:
    print("❌ Strategy generation failed.")
