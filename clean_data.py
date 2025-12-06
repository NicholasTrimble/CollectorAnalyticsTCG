import json
import os

RAW_FILE = "data/artifact_mythics_raw.json"
CLEANED_FILE = "data/artifact_mythics_cleaned.json"


def load_raw_data(filepath: str) -> dict:
    """Load raw JSON data from the specified file."""
    with open(filepath, "r") as f:
        return json.load(f)
    
def clean_card(card: dict) -> dict:
    """Extract and return relevant fields from a card dictionary."""
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
    """Saved the cleaned data for future use."""
    with open(file_path, "w") as f:
        json.dump(clean_list, f, indent=4)

def main():
    print("🔍 Loading raw data...")
    data = load_raw_data(RAW_FILE)

    cards = data.get("data", [])
    print(f"📦 Found {len(cards)} cards to clean.")

    cleaned_cards = [clean_card(card) for card in cards]

    save_clean_data(cleaned_cards, CLEANED_FILE)
    print(f"💾 Cleaned data saved to: {CLEANED_FILE}")

if __name__ == "__main__":
    main()