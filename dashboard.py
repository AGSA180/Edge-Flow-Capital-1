import yfinance as yf
import pandas as pd

# تحميل بيانات سهم تسلا
data = yf.download("TSLA", period="5d", interval="1h")

# إضافة قوة الإشارة (مثال)
data["signal_strength"] = 80

# حفظ البيانات
data.to_csv("signals.csv", index=False)

print("Market analysis completed")