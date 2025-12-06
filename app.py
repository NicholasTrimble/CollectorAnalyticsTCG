import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/cards"

st.set_page_config(page_title="Collector Analytics", layout="wide")

st.title("🃏 Collector Analytics Dashboard")
st.subheader("MTG Market Intelligence -Artifact Mythics")

@st.cache_data
def load_data():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()  # raises error if API fails
        
        data = response.json()

        if "results" not in data:
            st.error("⚠ API returned unexpected data format.")
            return []

        return data["results"]

    except Exception as e:
        st.error(f" Failed to load data: {e}")
        return []

cards = load_data()

search = st.text_input("Search Cards by Name:", "")
if search:
    cards = [card for card in cards if search.lower() in card["name"].lower()]
st.write(f"### Found {len(cards)} cards matching '{search}'")
st.dataframe(cards)