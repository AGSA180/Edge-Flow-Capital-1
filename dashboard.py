import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Edge Flow Capital", layout="wide")
st.title("📊 Edge Flow Capital — Dashboard")

if not os.path.exists("signals.csv"):
    st.warning("⚠️ لا توجد بيانات — شغّل GitHub Actions أولاً.")
    st.stop()

data = pd.read_csv("signals.csv")
data.columns = [str(col).split(",")[0].strip("('\" ") for col in data.columns]

if "Close" not in data.columns:
    st.error(f"❌ أعمدة الملف: {data.columns.tolist()}")
    st.stop()

data = data.dropna(subset=["Close"])

col1, col2, col3, col4 = st.columns(4)
col1.metric("آخر سعر", f"${data['Close'].iloc[-1]:.2f}")
col2.metric("أعلى سعر", f"${data['High'].max():.2f}" if "High" in data.columns else "N/A")
col3.metric("أدنى سعر", f"${data['Low'].min():.2f}" if "Low" in data.columns else "N/A")
col4.metric("عدد الصفوف", len(data))

st.line_chart(data["Close"])
st.dataframe(data, use_container_width=True)
