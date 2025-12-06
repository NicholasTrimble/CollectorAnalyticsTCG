import sqlite3

DB_FILE = "data/cards.db"

def run_query(query: str):
    """Execute the given SQL query and return the results."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

def format_price(value):
    if value is None:
        return "$0.00"
    return f"${value:.2f}"


def main():
    print("Example Query: All card names sorted alphabetically")

    results = run_query("""
                        SELECT name, usd_price 
                        FROM cards
                        ORDER BY name ASC
                        LIMIT 10;
                        """)
    
    for name, price in results:
        print(f"Name: {name}, Price: {format_price(price)} USD")

if __name__ == "__main__":
    main()
