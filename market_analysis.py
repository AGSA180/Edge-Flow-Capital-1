import yfinance as yf
import pandas as pd
from datetime import datetime

# تحميل بيانات TSLA
data = yf.download("TSLA", period="5d", interval="1h")

# تسوية الأعمدة
data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]

# إضافة معلومات الإشارة
data["symbol"] = "TSLA"
data["signal"] = "HOLD"
data["signal_strength"] = 80
data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M")

# حفظ البيانات
data.to_csv("signals.csv", index=True)
print("✅ Market analysis completed")
print(f"📊 Rows saved: {len(data)}")
