import json
import os

RAW_FILE = "data/all_cards_raw.json"
CLEANED_FILE = "data/all_cards_cleaned.json"

def load_raw_data(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def clean_card(card: dict) -> dict:
    prices = card.get("prices", {})

    image_url = None
    if "image_uris" in card:
        image_url = card["image_uris"].get("normal")

    return {
        "id": card.get("id"),
        "name": card.get("name"),
        "released_at": card.get("released_at"),
        "set_name": card.get("set_name"),
        "collector_number": card.get("collector_number"),
        "rarity": card.get("rarity"),
        "type_line": card.get("type_line"),
        "usd_price": prices.get("usd"),
        "usd_foil_price": prices.get("usd_foil"),
        "image_url": image_url,
        "scryfall_uri": card.get("scryfall_uri")
    }

def save_clean_data(clean_list: list, file_path: str) -> None:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(clean_list, f, indent=2)

def main():
    print("Loading raw data...")
    data = load_raw_data(RAW_FILE)

    print(f"Found {len(data)} cards. Cleaning...")
    cleaned = [clean_card(card) for card in data]

    save_clean_data(cleaned, CLEANED_FILE)
    print(f"Saved cleaned dataset to {CLEANED_FILE}")

if __name__ == "__main__":
    main()
