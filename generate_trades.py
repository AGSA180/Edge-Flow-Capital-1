import pandas as pd
import os
from datetime import datetime

if not os.path.exists("signals.csv"):
    print("❌ signals.csv not found")
    exit(1)

signals = pd.read_csv("signals.csv")

# تحديد عمود السعر تلقائياً
price_col = None
for col in ['Close', 'close', 'price', 'Price']:
    if col in signals.columns:
        price_col = col
        break

if price_col is None:
    print(f"❌ Column 'Close' not found")
    print(f"Available columns: {signals.columns.tolist()}")
    exit(1)

signals = signals.dropna(subset=[price_col])

trades = []
for _, row in signals.iterrows():
    entry = float(row[price_col])
    trades.append({
        "ticker":          "TSLA",
        "entry":           round(entry, 2),
        "tp1":             round(entry * 1.05, 2),
        "tp2":             round(entry * 1.10, 2),
        "tp3":             round(entry * 1.15, 2),
        "stop":            round(entry * 0.97, 2),
        "signal_strength": row.get("signal_strength", 80),
        "timestamp":       datetime.now().strftime("%Y-%m-%d %H:%M")
    })

import pandas as pd
trades_df = pd.DataFrame(trades)
trades_df.to_csv("trades.csv", index=False)

print(f"✅ Trade generation completed")
print(f"📈 Total trades: {len(trades)}")



