from tvdatafeed import TvDatafeed, Interval
import pandas as pd
import pandas_ta as ta
import os
from datetime import datetime

# ══════════════════════════════════════
# الاتصال بـ TradingView
# ══════════════════════════════════════
tv = TvDatafeed()  # بدون تسجيل دخول

# ══════════════════════════════════════
# قائمة الأسهم والمؤشرات
# ══════════════════════════════════════
WATCHLIST = [
    {"symbol": "TSLA",  "exchange": "NASDAQ"},
    {"symbol": "AAPL",  "exchange": "NASDAQ"},
    {"symbol": "NVDA",  "exchange": "NASDAQ"},
    {"symbol": "SPY",   "exchange": "AMEX"},
    {"symbol": "QQQ",   "exchange": "NASDAQ"},
    {"symbol": "AMZN",  "exchange": "NASDAQ"},
    {"symbol": "MSFT",  "exchange": "NASDAQ"},
    {"symbol": "META",  "exchange": "NASDAQ"},
]

# ══════════════════════════════════════
# إعدادات الاستراتيجية
# ══════════════════════════════════════
ATR_LENGTH    = 14
EMA_LENGTH    = 200
LIQ_LOOKBACK  = 20
TP1_MULTI     = 1.0
TP2_MULTI     = 2.0
TP3_MULTI     = 3.0
SL_MULTI      = 1.0
PO3_ACCUM     = 0.003
PO3_MANIP_H   = 1.001
PO3_MANIP_L   = 0.999

# ══════════════════════════════════════
# دالة تحليل سهم واحد
# ══════════════════════════════════════
def analyze(symbol, exchange):
    try:
        # سحب البيانات من TradingView
        df = tv.get_hist(
            symbol=symbol,
            exchange=exchange,
            interval=Interval.in_1_hour,
            n_bars=300
        )

        if df is None or len(df) < 210:
            print(f"⚠️ بيانات غير كافية: {symbol}")
            return None

        df.columns = [c.lower() for c in df.columns]
        df = df.rename(columns={"open":"open","high":"high","low":"low","close":"close","volume":"volume"})

        # ══════════════════════════════
        # المؤشرات
        # ══════════════════════════════
        df["atr"]    = ta.atr(df["high"], df["low"], df["close"], length=ATR_LENGTH)
        df["ema200"] = ta.ema(df["close"], length=EMA_LENGTH)
        df["atr_ma"] = df["atr"].rolling(20).mean()

        df["highest"] = df["high"].rolling(LIQ_LOOKBACK).max()
        df["lowest"]  = df["low"].rolling(LIQ_LOOKBACK).min()

        # EQH / EQL
        df["eqh"] = df["high"].where(df["high"] == df["highest"]).ffill()
        df["eql"] = df["low"].where(df["low"]  == df["lowest"]).ffill()

        # FVG
        df["fvg_bull"] = (df["low"].shift(2) > df["high"].shift(1)) & \
                         (df["low"].shift(2) < df["high"])
        df["fvg_bear"] = (df["high"].shift(2) < df["low"].shift(1)) & \
                         (df["high"].shift(2) > df["low"])

        # Power of Three
        df["is_accum"] = (df["high"] - df["low"]) / df["low"] < PO3_ACCUM
        df["is_manip"] = (df["high"].shift(1) > df["highest"].shift(1) * PO3_MANIP_H) | \
                         (df["low"].shift(1)  < df["lowest"].shift(1)  * PO3_MANIP_L)
        df["is_exp"]   = (df["close"] > df["highest"].shift(1) * PO3_MANIP_H) | \
                         (df["close"] < df["lowest"].shift(1)  * PO3_MANIP_L)

        # ══════════════════════════════
        # شروط الدخول
        # ══════════════════════════════
        last = df.iloc[-1]
        prev = df.iloc[-2]

        above_ema = last["close"] > last["ema200"]
        below_ema = last["close"] < last["ema200"]

        raw_long  = (last["is_exp"] and
                     last["close"] > last["open"] and
                     (last["fvg_bull"] or last["close"] > last["eqh"]) and
                     above_ema)

        raw_short = (last["is_exp"] and
                     last["close"] < last["open"] and
                     (last["fvg_bear"] or last["close"] < last["eql"]) and
                     below_ema)

        prev_long  = (prev["is_exp"] and
                      prev["close"] > prev["open"] and
                      (prev["fvg_bull"] or prev["close"] > prev["eqh"]) and
                      prev["close"] > prev["ema200"])

        prev_short = (prev["is_exp"] and
                      prev["close"] < prev["open"] and
                      (prev["fvg_bear"] or prev["close"] < prev["eql"]) and
                      prev["close"] < prev["ema200"])

        long_signal  = raw_long  and not prev_long
        short_signal = raw_short and not prev_short

        if not long_signal and not short_signal:
            return None

        # ══════════════════════════════
        # نظام تقييم الجودة
        # ══════════════════════════════
        atr   = last["atr"]
        close = last["close"]

        candle_body  = abs(last["close"] - last["open"])
        candle_range = last["high"] - last["low"]
        score_candle = 1 if (candle_range > 0 and candle_body / candle_range > 0.6) else 0
        score_atr    = 1 if (atr > last["atr_ma"] * 1.1) else 0
        score_ema    = 1 if (long_signal and above_ema) or (short_signal and below_ema) else 0
        score_manip  = 2 if last["is_manip"] else 0
        score_fvg    = 2 if (long_signal and last["fvg_bull"]) or (short_signal and last["fvg_bear"]) else 0
        score_liq    = 2 if (long_signal and last["close"] > last["eqh"]) or \
                            (short_signal and last["close"] < last["eql"]) else 0
        score_session = 1

        quality = score_fvg + score_liq + score_manip + score_candle + score_atr + score_ema + score_session

        # تقييم نصي
        if quality >= 9:
            quality_label = "🔥🔥🔥 ممتاز جداً"
        elif quality >= 7:
            quality_label = "🔥🔥 ممتاز"
        elif quality >= 5:
            quality_label = "⭐⭐ جيد"
        elif quality >= 3:
            quality_label = "⚠️ ضعيفة"
        else:
            quality_label = "❌ لا تدخل"

        # ══════════════════════════════
        # الأهداف والوقف
        # ══════════════════════════════
        direction = "كول" if long_signal else "بوت"
        strike    = round(close / 5) * 5

        if long_signal:
            tp1 = round(close + atr * TP1_MULTI, 2)
            tp2 = round(close + atr * TP2_MULTI, 2)
            tp3 = round(close + atr * TP3_MULTI, 2)
            sl  = round(close - atr * SL_MULTI,  2)
        else:
            tp1 = round(close - atr * TP1_MULTI, 2)
            tp2 = round(close - atr * TP2_MULTI, 2)
            tp3 = round(close - atr * TP3_MULTI, 2)
            sl  = round(close + atr * SL_MULTI,  2)

        rr = round(TP1_MULTI / SL_MULTI, 2)

        return {
            "symbol":        symbol,
            "direction":     direction,
            "strike":        strike,
            "entry":         round(close, 2),
            "tp1":           tp1,
            "tp2":           tp2,
            "tp3":           tp3,
            "sl":            sl,
            "rr":            rr,
            "atr":           round(atr, 2),
            "quality":       quality,
            "quality_label": quality_label,
            "fvg":           "✅" if score_fvg  == 2 else "❌",
            "sweep":         "✅" if score_liq  == 2 else "❌",
            "manip":         "✅" if score_manip == 2 else "❌",
            "ema":           "✅" if score_ema  == 1 else "❌",
            "timestamp":     datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

    except Exception as e:
        print(f"❌ خطأ في {symbol}: {e}")
        return None

# ══════════════════════════════════════
# تشغيل التحليل على كل الأسهم
# ══════════════════════════════════════
signals = []
for stock in WATCHLIST:
    print(f"🔍 تحليل {stock['symbol']}...")
    result = analyze(stock["symbol"], stock["exchange"])
    if result:
        signals.append(result)
        print(f"✅ إشارة: {result['symbol']} — {result['direction']} — جودة: {result['quality']}/10")

# ══════════════════════════════════════
# حفظ النتائج
# ══════════════════════════════════════
if signals:
    df_signals = pd.DataFrame(signals)
    df_signals.to_csv("signals.csv", index=False)
    print(f"\n✅ تم حفظ {len(signals)} إشارة في signals.csv")
else:
    # حفظ ملف فارغ بالأعمدة الصحيحة
    pd.DataFrame(columns=[
        "symbol","direction","strike","entry",
        "tp1","tp2","tp3","sl","rr","atr",
        "quality","quality_label","fvg","sweep",
        "manip","ema","timestamp"
    ]).to_csv("signals.csv", index=False)
    print("⚠️ لا توجد إشارات الآن")
```

---

## 📦 أضف لـ `requirements.txt`:
```
streamlit
pandas
tvdatafeed
pandas_ta
