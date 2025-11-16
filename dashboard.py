import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("Testing")

df = pd.DataFrame({
    "Height": [1.8, 1.9, 1.6],
    "Dick Size": [1.8, 1.9, 1.6],
})

st.bar_chart(df)