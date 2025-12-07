import requests
import json
import os

BULK_URL = "https://api.scryfall.com/bulk-data"
OUTPUT_DIR = "data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "all_cards_raw.json")


def fetch_bulk_metadata():
    """Get the list of available bulk files and return the oracle_cards entry."""
    response = requests.get(BULK_URL)
    response.raise_for_status()

    bulk_files = response.json()["data"]

    oracle_file = next(
        (item for item in bulk_files if item["type"] == "oracle_cards"),
        None
    )

    if not oracle_file:
        raise RuntimeError("Oracle bulk file not found in Scryfall bulk data!")

    return oracle_file["download_uri"]


def download_bulk_json(download_url: str):
    """Download the full JSON file of cards."""
    print("Downloading bulk Oracle card data...")

    response = requests.get(download_url)
    response.raise_for_status()

    return response.json()


def save_json(data, filepath: str):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main():
    print("Fetching bulk metadata...")
    download_url = fetch_bulk_metadata()
    print(f"Bulk download URL: {download_url}")

    cards = download_bulk_json(download_url)
    print(f"Total cards received: {len(cards)}")

    save_json(cards, OUTPUT_FILE)
    print(f"Saved raw card data to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
