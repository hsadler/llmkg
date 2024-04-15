import nltk
import streamlit as st

st.set_page_config(
    page_title="Stemming POC",
    page_icon="🧠",
    layout="wide",
)
st.title("Test Stemming")

word = st.text_input("Enter a word to stem", "")
if word:
    st.write(f"Stemmed word: {nltk.stem.PorterStemmer().stem(word)}")
