import streamlit as st
import pandas as pd
import os

st.title("Edge Flow Capital Dashboard")

# إنشاء الملف إذا ما كان موجوداً
if not os.path.exists("signals.csv"):
    df_empty = pd.DataFrame(columns=[
        'symbol', 'signal', 'price', 'timestamp', 'confidence'
    ])
    df_empty.to_csv("signals.csv", index=False)
    st.warning("⚠️ لا توجد إشارات حتى الآن — في انتظار التحليل.")
else:
    data = pd.read_csv("signals.csv")
    if data.empty:
        st.info("📭 الملف موجود لكن لا توجد إشارات بعد.")
    else:
        st.dataframe(data)
