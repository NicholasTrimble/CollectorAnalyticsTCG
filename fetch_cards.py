import json
import os
import requests


API_URL = "https://api.scryfall.com/cards/search"
Search_QUERY = "type:artifact rarity:mythic"

OUTPUT_DIR = "data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "artifact_mythics_raw.json")


def fetch_cards(query: str) -> dict:
    """Fetch cards from Scryfall API based on the given query."""
    params = {"q": query}
    response = requests.get(API_URL, params=params)
    response.raise_for_status()
    return response.json()

def save_json(data: dict, filepath: str):
    """Save the given data as a JSON file."""
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)

def main():
    print(f"Fetching cards with query: {Search_QUERY}")
    data = fetch_cards(Search_QUERY)

    print("Request completed successfully.")
    print(f"Cards returned: {data.get('total_cards', 'Unknown')}")

    save_json(data, OUTPUT_FILE)
    print(f"Data saved to {OUTPUT_FILE}")

    if "data" in data and len(data["data"]) > 0:
        first_card = data["data"][0]
        print("\n-Preview-")
        print(f"Name: {first_card.get('name', 'N/A')}")
        print(f"Set: {first_card.get('set_name', 'N/A')}")
        print(f"Rarity: {first_card.get('rarity', 'N/A')}")
        print(f"Type: {first_card.get('type_line', 'N/A')}")
        print(f"Image URL: {first_card.get('image_uris', {}).get('normal', 'N/A')}")
        print(f"Price: {first_card.get('prices', {}).get('usd', 'N/A')} USD ")

if __name__ == "__main__":
    main()    

