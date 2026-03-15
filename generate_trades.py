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

data = data.dropna(subset=["




