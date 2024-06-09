import requests
import streamlit as st
from openai import OpenAI

openai_client = OpenAI(
    api_key="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"
)

PAGE_TITLE: str = "Subject populator via ChatGPT"
BE_HOST: str = "http://localhost:8000"

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon="♻️",
    layout="wide",
)
st.title(PAGE_TITLE)

status_res = requests.get(f"{BE_HOST}/status")
if status_res.status_code != 200:
    st.error("Backend is not available.")
    st.stop()

st.write(f"Backend is available at {BE_HOST} with status: `{status_res.json()['status']}`")
