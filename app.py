import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/cards"

st.set_page_config(page_title="Collector Analytics", layout="wide")

st.title("🃏 Collector Analytics Dashboard")
st.caption("MTG Market Intelligence — Artifact Mythics")


@st.cache_data
def fetch_cards(params=None):
    response = requests.get(API_URL, params=params)
    response.raise_for_status()
    return response.json()["results"]


st.sidebar.header("🔧 Filters")

search = st.sidebar.text_input("Search card name")
rarity = st.sidebar.selectbox("Rarity", ["", "mythic", "rare", "uncommon", "common"])

sort_options = {
    "None": None,
    "Name (A-Z)": ("name", "asc"),
    "Name (Z-A)": ("name", "desc"),
    "Price (Low → High)": ("usd_price", "asc"),
    "Price (High → Low)": ("usd_price", "desc"),
}

sort_label = st.sidebar.selectbox("Sort by", list(sort_options.keys()))
sort, order = sort_options[sort_label] if sort_label != "None" else (None, None)


params = {}

if search:
    params["search"] = search

if rarity:
    params["rarity"] = rarity

if sort:
    params["sort"] = sort
    params["order"] = order


cards = fetch_cards(params)


st.write(f"Showing **{len(cards)} cards**")

if cards:
    highest = max(cards, key=lambda c: c["usd_price"] or 0)
    avg_price = sum((c["usd_price"] or 0) for c in cards) / len(cards)

    col1, col2 = st.columns(2)
    col1.metric("💰 Highest Price", f"${highest['usd_price']:.2f}", highest["name"])
    col2.metric("📊 Avg Price", f"${avg_price:.2f}")


import pandas as pd

df = pd.DataFrame(cards)

st.dataframe(df[["name", "usd_price", "rarity", "set_name"]], use_container_width=True)

selected_name = st.selectbox("📌 Select a card to view details:", df["name"].tolist())

selected_card = next(card for card in cards if card["name"] == selected_name)


# Detailed View
st.subheader(f"🧾 Details for: {selected_card['name']}")

col1, col2 = st.columns([1, 2])

with col1:
    if selected_card["image_url"]:
        st.image(selected_card["image_url"], caption=selected_card["name"])
    else:
        st.text("No Image Available")

with col2:
    st.write(f"**Set:** {selected_card['set_name']}")
    st.write(f"**Collector #:** {selected_card['collector_number']}")
    st.write(f"**Rarity:** {selected_card['rarity'].capitalize()}")
    st.write(f"**Type:** {selected_card['type_line']}")
    
    usd = selected_card['usd_price'] or 0
    foil = selected_card['usd_foil_price'] or 0

    st.write(f"**Price:** ${usd:.2f}")
    st.write(f"**Foil Price:** ${foil:.2f}")

    st.markdown(f"[View on Scryfall]({selected_card['scryfall_uri']})")
