import streamlit as st
import pandas as pd

st.title("Edge Flow Capital Dashboard")

data = pd.read_csv("signals.csv")

st.dataframe(data)