from backtest_engine.engine_bt import run_backtest_from_json

summary, result = run_backtest_from_json("strategies/generated/sample_strategy.json", ticker="AAPL")

print("📈 Strategy Performance Summary:")
for k, v in summary.items():
    print(f"{k}: {v}")

result.plot()