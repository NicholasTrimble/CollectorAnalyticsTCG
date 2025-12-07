import sqlite3
import json
import os

DB_FILE = "data/cards.db"
CLEANED_FILE = "data/all_cards_cleaned.json"

os.makedirs("data", exist_ok=True)

def load_clean_data(filepath: str) -> list[dict]:
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def create_tables(conn):
    conn.execute("""
    CREATE TABLE IF NOT EXISTS cards (
        id TEXT PRIMARY KEY,
        name TEXT,
        released_at TEXT,
        set_name TEXT,
        collector_number TEXT,
        rarity TEXT,
        type_line TEXT,
        usd_price REAL,
        usd_foil_price REAL,
        image_url TEXT,
        scryfall_uri TEXT
    );
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS favorites (
        id TEXT PRIMARY KEY,
        added_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

def insert_card(conn, card: dict):
    conn.execute("""
    INSERT OR REPLACE INTO cards (
        id, name, released_at, set_name, collector_number,
        rarity, type_line, usd_price, usd_foil_price,
        image_url, scryfall_uri
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (
        card["id"],
        card["name"],
        card["released_at"],
        card["set_name"],
        card["collector_number"],
        card["rarity"],
        card["type_line"],
        float(card["usd_price"]) if card["usd_price"] else None,
        float(card["usd_foil_price"]) if card["usd_foil_price"] else None,
        card["image_url"],
        card["scryfall_uri"]
    ))

def main():
    print("Loading cleaned data...")
    cards = load_clean_data(CLEANED_FILE)

    conn = sqlite3.connect(DB_FILE)
    create_tables(conn)

    print(f"Inserting {len(cards)} cards...")
    for i, card in enumerate(cards, start=1):
        insert_card(conn, card)
        if i % 5000 == 0:
            conn.commit()
            print(f"{i} inserted...")

    conn.commit()
    conn.close()
    print(f"Database ready: {DB_FILE}")

if __name__ == "__main__":
    main()
