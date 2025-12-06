from fastapi import FastAPI, Query, HTTPException
import sqlite3

DB_FILE = "data/cards.db"

app = FastAPI(title="Card Price API")

def query_cards(rarity: str = None, sort: str = None, order: str = "asc", search: str = None):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    base_query = "SELECT * FROM cards"
    filters = []
    params = []

    if rarity:
        filters.append("rarity = ?")
        params.append(rarity)

    if search:
        filters.append("name LIKE ?")
        params.append(f"%{search}%")

    if filters:
        base_query += " WHERE " + " AND ".join(filters)

    if sort:
        base_query += f" ORDER BY {sort} {order.upper()}"

    cursor.execute(base_query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.post("/favorites/{card_id}")
def add_favorite(card_id: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO favorites (id) VALUES (?)", (card_id,))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Card already in favorites")
    conn.close()
    return {"message": "Card added to favorites", "card_id": card_id}

@app.delete("/favorites/{card_id}")
def remove_favorite(card_id: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM favorites WHERE id = ?", (card_id,))
    conn.commit()
    conn.close()
    return {"message": "Card removed from favorites", "card_id": card_id}

@app.get("/favorites")
def list_favorites():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.* FROM cards c
        JOIN favorites f ON c.id = f.id
    """)
    rows = cursor.fetchall()
    conn.close()
    return {"count": len(rows), "results": [dict(r) for r in rows]}


@app.get("/cards")
def read_cards(
    rarity: str | None = Query(default=None),
    sort: str | None = Query(default=None),
    order: str | None = Query(default="asc"),
    search: str | None = Query(default=None)
):
    results = query_cards(rarity, sort, order, search)
    return {"count": len(results), "results": results}
