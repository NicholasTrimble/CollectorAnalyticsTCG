import streamlit as st
import pandas as pd
import json
import altair as alt
import os

DATA_FILE = "data/all_cards_cleaned.json"

st.set_page_config(page_title="Collector Analytics", layout="wide")

# --- Load Data ---
@st.cache_data
def load_cards():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

cards = load_cards()

# Convert to DataFrame for filtering
df = pd.DataFrame(cards)

# --- UI ---
st.title("Collector Analytics Dashboard")
st.caption("MTG Market Intelligence — Full Dataset")

view_mode = st.sidebar.radio("View Mode", ["All Cards", "Favorites"])

# Local stored favorites (no backend)
if "favorites" not in st.session_state:
    st.session_state.favorites = set()

st.sidebar.subheader("Filters")

search = st.sidebar.text_input("Search card name")
rarity = st.sidebar.selectbox("Rarity", ["", "mythic", "rare", "uncommon", "common"])

sort_options = {
    "None": None,
    "Name (A-Z)": ("name", True),
    "Name (Z-A)": ("name", False),
    "Price (Low → High)": ("usd_price", True),
    "Price (High → Low)": ("usd_price", False),
}

sort_label = st.sidebar.selectbox("Sort by", list(sort_options.keys()))
sort_choice = sort_options[sort_label]

# --- Filtering logic ---
filtered = df.copy()

if search:
    filtered = filtered[filtered["name"].str.contains(search, case=False, na=False)]

if rarity:
    filtered = filtered[filtered["rarity"] == rarity]

if view_mode == "Favorites":
    filtered = filtered[filtered["id"].isin(st.session_state.favorites)]

if sort_choice:
    key, asc = sort_choice
    filtered = filtered.sort_values(by=key, ascending=asc)

# --- Results ---
st.write(f"Showing {len(filtered)} cards")

if len(filtered) == 0:
    st.warning("No results match your filters.")
    st.stop()

# Metrics


filtered["usd_price"] = pd.to_numeric(filtered["usd_price"], errors="coerce")

if filtered["usd_price"].dropna().empty:
    highest_price = 0
    highest_name = "No priced cards"
    avg_price = 0
else:
    highest_price = filtered["usd_price"].max()
    highest_row = filtered.loc[filtered["usd_price"] == highest_price].iloc[0]
    highest_name = highest_row["name"]
    avg_price = filtered["usd_price"].mean()

col1, col2 = st.columns(2)
col1.metric("Highest Price", f"${highest_price:.2f}", highest_name)
col2.metric("Average Price", f"${avg_price:.2f}")


# --- Table + card detail ---
st.subheader("Browse Cards")

subset = filtered[["name", "usd_price", "rarity", "set_name"]]
selected = st.dataframe(subset, on_select="rerun", use_container_width=True)

if hasattr(selected, "selection") and selected.selection.rows:
    selected_index = selected.selection.rows[0]
    selected_card = filtered.iloc[selected_index].to_dict()
else:
    selected_card = filtered.iloc[0].to_dict()

st.subheader(f"Details: {selected_card['name']}")
card_cols = st.columns([1, 2])

with card_cols[0]:
    if selected_card["image_url"]:
        st.image(selected_card["image_url"], use_container_width=True)
    else:
        st.text("No Image Available")

with card_cols[1]:
    st.write(f"Set: {selected_card['set_name']}")
    st.write(f"Collector #: {selected_card['collector_number']}")
    st.write(f"Rarity: {selected_card['rarity']}")
    st.write(f"Type: {selected_card['type_line']}")
    st.write(f"Price: ${selected_card['usd_price'] or 0:.2f}")
    st.write(f"Foil Price: ${selected_card['usd_foil_price'] or 0:.2f}")
    st.markdown(f"[View on Scryfall]({selected_card['scryfall_uri']})")


# --- Price Distribution ---
st.subheader("Price Distribution")
chart = alt.Chart(filtered).mark_bar().encode(
    alt.X("usd_price", bin=alt.Bin(maxbins=30), title="Price USD"),
    alt.Y("count()", title="Card Count")
).properties(height=300)

st.altair_chart(chart, use_container_width=True)



# --- Favorites ---
if selected_card["id"] in st.session_state.favorites:
    if st.button("Remove from Watchlist"):
        st.session_state.favorites.remove(selected_card["id"])
else:
    if st.button("Add to Watchlist"):
        st.session_state.favorites.add(selected_card["id"])


# adding dark mode toggle
theme_choice = st.sidebar.radio("Theme", ["Dark", "Light"])

if theme_choice == "Dark":
    st.write("<style>body { background-color: black; color: white; }</style>", unsafe_allow_html=True)
