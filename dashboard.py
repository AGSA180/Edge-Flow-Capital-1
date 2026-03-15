import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Edge Flow Capital", layout="wide")
st.title("📊 Edge Flow Capital — Dashboard")

if not os.path.exists("signals.csv"):
    st.warning("⚠️ لا توجد بيانات — شغّل GitHub Actions أولاً.")
    st.stop()

data = pd.read_csv("signals.csv")

# تحديد عمود السعر تلقائياً
price_col = None
for col in ['Close', 'close', 'price', 'Price']:
    if col in data.columns:
        price_col = col
        break

if price_col is None:
    st.error(f"❌ أعمدة الملف: {data.columns.tolist()}")
    st.stop()

data = data.dropna(subset=[price_col])

if data.empty:
    st.warning("⚠️ الملف فارغ.")
    st.stop()

col1, col2, col3, col4 = st.columns(4)
col1.metric("آخر سعر",   f"${float(data[price_col].iloc[-1]):.2f}")
col2.metric("أعلى سعر",  f"${float(data[price_col].max()):.2f}")
col3.metric("أدنى سعر",  f"${float(data[price_col].min()):.2f}")
col4.metric("عدد الصفوف", len(data))

st.line_chart(data[price_col])
st.dataframe(data, use_container_width=True)
