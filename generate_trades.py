import pandas as pd

signals = pd.read_csv("signals.csv")

trades = []

for index,row in signals.iterrows():

    entry = row["Close"]

    trade = {
        "ticker": "TSLA",
        "entry": round(entry,2),
        "tp1": round(entry*1.05,2),
        "tp2": round(entry*1.10,2),
        "tp3": round(entry*1.15,2),
        "stop": round(entry*0.97,2),
        "signal_strength": row["signal_strength"]
    }

    trades.append(trade)

print(trades)