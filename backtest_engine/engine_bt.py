import yfinance as yf
import pandas as pd
import bt
import json
from utils.indicators import calculate_rsi, calculate_sma, calculate_bollinger_bands, calculate_macd
import re

def fetch_price_data(ticker, start="2020-01-01", end="2024-12-31"):
    df = yf.download(ticker, start=start, end=end)

    if df.empty:
        raise ValueError(f"No data found for {ticker}")

    # Flatten columns if multi-indexed
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ['_'.join(col).strip() for col in df.columns.values]

    # Try various Close column names
    possible_close_names = [
        "Close",
        f"{ticker} Close",
        f"Close_{ticker}",
        f"{ticker}_Close"
    ]

    for col in possible_close_names:
        if col in df.columns:
            close = df[col]
            close.name = ticker  # set proper name for later DataFrame creation
            return close

    raise ValueError(f"Could not find a 'Close' column for {ticker}. Available columns: {df.columns.tolist()}")


def apply_indicators(price, strategy):
    indicators = {}

    all_conditions = strategy["entry_conditions"] + strategy["exit_conditions"]

    for cond in all_conditions:
        # Detect RSI(x)
        rsi_match = re.search(r"RSI\((\d+)\)", cond)
        if rsi_match:
            period = int(rsi_match.group(1))
            if "RSI" not in indicators:
                indicators["RSI"] = calculate_rsi(price, period)

        # Detect SMA(x)
        sma_matches = re.findall(r"SMA\((\d+)\)", cond)
        for period_str in sma_matches:
            period = int(period_str)
            key = f"SMA{period}"
            if key not in indicators:
                indicators[key] = calculate_sma(price, period)

        # Detect Bollinger Bands
        if "Lower Bollinger Band" in cond or "Upper Bollinger Band" in cond:
            if "BollingerLower" not in indicators or "BollingerUpper" not in indicators:
                upper, lower = calculate_bollinger_bands(price)
                indicators["BollingerUpper"] = upper
                indicators["BollingerLower"] = lower
        
        if "MACD" in cond:
            if "MACD" not in indicators:
                macd, signal = calculate_macd(price)
                indicators["MACD"] = macd
                indicators["Signal"] = signal

    return indicators

def evaluate_condition(cond: str, price: pd.Series, indicators: dict, idx: int) -> bool:
    try:
        if "RSI" in cond:
            val = indicators["RSI"].iloc[idx]
            if "<" in cond:
                threshold = int(cond.split("<")[1].strip())
                return val < threshold
            elif ">" in cond:
                threshold = int(cond.split(">")[1].strip())
                return val > threshold

        elif "SMA" in cond:
            if "crosses above" in cond:
                short_period = int(cond.split("SMA(")[1].split(")")[0])
                long_period = int(cond.split("SMA(")[2].split(")")[0])
                short = indicators[f"SMA{short_period}"]
                long = indicators[f"SMA{long_period}"]
                return short.iloc[idx - 1] < long.iloc[idx - 1] and short.iloc[idx] > long.iloc[idx]

        elif "Price < Lower Bollinger Band" in cond:
            return price.iloc[idx] < indicators["BollingerLower"].iloc[idx]

        elif "Price > Upper Bollinger Band" in cond:
            return price.iloc[idx] > indicators["BollingerUpper"].iloc[idx]
        
        elif "MACD > Signal" in cond:
            return indicators["MACD"].iloc[idx] > indicators["Signal"].iloc[idx]

        elif "MACD < Signal" in cond:
            return indicators["MACD"].iloc[idx] < indicators["Signal"].iloc[idx]

        elif "price touches upper bollinger band" in cond:
            return price.iloc[idx] >= indicators["BollingerUpper"].iloc[idx]

        elif "price touches lower bollinger band" in cond:
            return price.iloc[idx] <= indicators["BollingerLower"].iloc[idx]

    except:
        return False

    return False

def strategy_logic_from_json(price: pd.Series, indicators: dict, strategy: dict):
    signals = pd.Series(index=price.index, data=0.0)

    for i in range(1, len(price)):
        entry_met = all(evaluate_condition(cond, price, indicators, i) for cond in strategy["entry_conditions"])
        exit_met = any(evaluate_condition(cond, price, indicators, i) for cond in strategy["exit_conditions"])

        if entry_met:
            signals.iloc[i] = 1.0
        elif exit_met:
            signals.iloc[i] = 0.0
        else:
            signals.iloc[i] = signals.iloc[i - 1]  # Hold

    return signals

def run_backtest_from_json(json_path: str, ticker="AAPL"):
    with open(json_path, "r") as f:
        strategy = json.load(f)

    price = fetch_price_data(ticker)
    indicators = apply_indicators(price, strategy)
    signals = strategy_logic_from_json(price, indicators, strategy)

    print("✅ Price Data Loaded:")
    print(price.head())

    # Combine signals with price
    data = pd.DataFrame({price.name: price}).dropna()
    weights = pd.DataFrame({price.name: signals}).dropna()

    print("📊 Entry/Exit Signals Preview:")
    print(signals.value_counts())

    strat = bt.Strategy(strategy["strategy_name"], [
        bt.algos.RunDaily(),
        bt.algos.SelectAll(),
        bt.algos.WeighTarget(weights),
        bt.algos.Rebalance()
    ])

    portfolio = bt.Backtest(strat, data)
    result = bt.run(portfolio)[0]

    stats = result.stats
    summary = {
        "strategy_name": strategy["strategy_name"],
        "sharpe": stats["daily_sharpe"],
        "cagr": stats["cagr"],
        "max_drawdown": stats["max_drawdown"],
        "total_return": stats["total_return"],
    }

    return summary, result
    


