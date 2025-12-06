from fastapi import FastAPI
import sqlite3

DB_FILE = "data/cards.db"

app = FastAPI(title="Card Price API")

def get_all_cards():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cards ORDER BY name ASC;")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/cards")
def read_cards():
    return{
        "count": len(get_all_cards()),
        "results": get_all_cards()
    }