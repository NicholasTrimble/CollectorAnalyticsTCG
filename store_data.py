import sqlite3
import json

CLEANED_FILE = "data/artifact_mythics_cleaned.json"
DB_FILE = "data/cards.db"

def load_clean_data(filepath: str) -> list[dict]:
    with open(filepath, "r") as f:
        return json.load(f)

def create_table(conn):
    """Creates the cards table if it does not already exist."""
    query = """
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
    """
    conn.execute(query)

def insert_card(conn, card: dict):
    """Insert a cleaned card record into the database."""
    query = """
    INSERT OR REPLACE INTO cards (
        id, name, released_at, set_name, collector_number,
        rarity, type_line, usd_price, usd_foil_price,
        image_url, scryfall_uri
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """
    values = (
        card["id"], card["name"], card["released_at"], card["set_name"],
        card["collector_number"], card["rarity"], card["type_line"],
        float(card["usd_price"]) if card["usd_price"] else None,
        float(card["usd_foil_price"]) if card["usd_foil_price"] else None,
        card["image_url"], card["scryfall_uri"]
    )
    conn.execute(query, values)

def main():
    print("Loading cleaned data...")
    cards = load_clean_data(CLEANED_FILE)

    print("Connecting to SQLite database...")
    conn = sqlite3.connect(DB_FILE)

    print("Creating table if needed...")
    create_table(conn)

    print("Inserting cards...")
    for card in cards:
        insert_card(conn, card)

    conn.commit()
    conn.close()
    print(f"Done! Stored {len(cards)} cards in {DB_FILE}")

if __name__ == "__main__":
    main()
