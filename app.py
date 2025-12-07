import streamlit as st
import requests
import pandas as pd
import altair as alt

API_URL = "http://127.0.0.1:8000/cards"
FAV_URL = "http://127.0.0.1:8000/favorites"

st.set_page_config(page_title="Collector Analytics", layout="wide")

# HEADER
st.title("Collector Analytics Dashboard")
st.caption("MTG Market Intelligence — Artifact Mythics")


# SIDEBAR NAVIGATION
view_mode = st.sidebar.radio(
    "View Mode",
    ["All Cards", "Favorites"]
)


# SIDEBAR FILTERS
params = {}
if view_mode == "All Cards":

    st.sidebar.header("Filters")

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

# Build params
    if search:
        params["search"] = search

    if rarity:
        params["rarity"] = rarity

    if sort:
        params["sort"] = sort
        params["order"] = order

# FETCH DATA
if view_mode == "Favorites":
    response = requests.get(FAV_URL)
else:
    response = requests.get(API_URL, params=params)

cards = response.json()["results"]


# EMPTY STATE
if len(cards) == 0:
    if view_mode == "Favorites":
        st.info("You haven't added any cards to your watchlist.")
    else:
        st.warning("No cards found. Try adjusting filters.")
    st.stop()


# METRICS
st.write(f"Showing **{len(cards)} cards**")

if cards:
    highest = max(cards, key=lambda c: (c["usd_price"] or 0))
    avg_price = sum((c["usd_price"] or 0) for c in cards) / len(cards)

    high_price = highest["usd_price"] or 0
    col1, col2 = st.columns(2)
    col1.metric("Highest Price", f"${high_price:.2f}", highest["name"])
    col2.metric("Avg Price", f"${avg_price:.2f}")



# Price Distribution Chart
df = pd.DataFrame(cards)
st.subheader("Price Distribution")
hist_chart = alt.Chart(df).mark_bar().encode(
    alt.X("usd_price", bin=alt.Bin(maxbins=30), title="Price (USD)"),
    alt.Y("count()", title="Number of Cards"),
).properties(height=300)
st.altair_chart(hist_chart, use_container_width=True)

# Most valuable cards
st.subheader("Top 10 Most Valuable Cards")
top10 = df.sort_values(by="usd_price", ascending=False).head(10)
top10_chart = alt.Chart(top10).mark_bar().encode(
    alt.X("name", sort=None, title="Card Name"),
    alt.Y("usd_price", title="Price (USD)"),
    tooltip=["name", "usd_price"]
).properties(height=400)
st.altair_chart(top10_chart, use_container_width=True)

# Rarity Breakdown Chart
st.subheader("Rarity Breakdown")
rarity_chart = alt.Chart(df).mark_bar().encode(
    alt.X("rarity", title="Rarity"),
    alt.Y("count()", title="Number of Cards"),
).properties(height=300)
st.altair_chart(rarity_chart, use_container_width=True)

# SELECTABLE TABLE
df = pd.DataFrame(cards)
subset = df[["name", "usd_price", "rarity", "set_name"]]

selected_rows = st.dataframe(
    subset,
    use_container_width=True,
    on_select="rerun"
)

if hasattr(selected_rows, "selection") and selected_rows.selection.rows:
    selected_index = selected_rows.selection.rows[0]
    selected_card = cards[selected_index]
else:
    selected_card = cards[0]


# DETAIL VIEW
st.subheader(f"Details: {selected_card['name']}")

c1, c2 = st.columns([1, 2])

with c1:
    if selected_card["image_url"]:
        st.image(selected_card["image_url"], use_container_width=True)
    else:
        st.text("No Image Available")

with c2:
    st.write(f"**Set:** {selected_card['set_name']}")
    st.write(f"**Collector #:** {selected_card['collector_number']}")
    st.write(f"**Rarity:** {selected_card['rarity'].capitalize()}")
    st.write(f"**Type:** {selected_card['type_line']}")

    usd = selected_card["usd_price"] or 0
    foil = selected_card["usd_foil_price"] or 0

    st.write(f"**Price:** ${usd:.2f}")
    st.write(f"**Foil Price:** ${foil:.2f}")

    st.markdown(f"[View on Scryfall]({selected_card['scryfall_uri']})")


# FAVORITE BUTTON
card_id = selected_card["id"]
fav_api = f"{FAV_URL}/{card_id}"

if view_mode == "Favorites":
    if st.button("Remove from Watchlist"):
        requests.delete(fav_api)
        st.success("Removed from watchlist.")
        st.experimental_rerun()
else:
    if st.button("Add to Watchlist"):
        requests.post(fav_api)
        st.success("Added to watchlist!")
        st.experimental_rerun()
