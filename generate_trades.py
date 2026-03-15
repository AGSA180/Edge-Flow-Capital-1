import pandas as pd
import os
from datetime import datetime

# قراءة الإشارات
if not os.path.exists("signals.csv"):
    print("❌ signals.csv not found")
    exit(1)

signals = pd.read_csv("signals.csv")

# التحقق من عمود Close
if "Close" not in signals.columns:
    print("❌ Column 'Close' not found")
    print("Available columns:", signals.columns.tolist())
    exit(1)

# إزالة الصفوف الفارغة
signals = signals.dropna(subset=["Close"])

trades = []
for index, row in signals.iterrows():
    entry = row["Close"]
    trade = {
        "ticker": "TSLA",
        "entry": round(entry, 2),
        "tp1": round(entry * 1.05, 2),
        "tp2": round(entry * 1.10, 2),
        "tp3": round(entry * 1.15, 2),
        "stop": round(entry * 0.97, 2),
        "signal_strength": row.get("signal_strength", 0),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    trades.append(trade)

# حفظ الصفقات
trades_df = pd.DataFrame(trades)
trades_df.to_csv("trades.csv", index=False)

print(f"✅ Trade generation completed")
print(f"📈 Total trades: {len(trades)}")
print(trades_df.head())
