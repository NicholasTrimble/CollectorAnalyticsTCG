from fastapi import FastAPI, Query, HTTPException
import sqlite3

DB_FILE = "data/cards.db"

app = FastAPI(title="Card Price API")

def query_cards(rarity=None, sort=None, order="asc", search=None, limit=50, offset=0):
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

    base_query += " LIMIT ? OFFSET ?"
    params += [limit, offset]

    cursor.execute(base_query, params)
    result = cursor.fetchall()

    conn.close()
    return [dict(r) for r in result]


@app.get("/cards")
def get_cards(
    rarity: str | None = Query(default=None),
    sort: str | None = Query(default=None),
    order: str | None = Query(default="asc"),
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=500)
):
    offset = (page - 1) * limit
    results = query_cards(rarity, sort, order, search, limit, offset)
    return {"count": len(results), "results": results}


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
    return {"message": "Added"}

@app.delete("/favorites/{card_id}")
def remove_favorite(card_id: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM favorites WHERE id = ?", (card_id,))
    conn.commit()
    conn.close()
    return {"message": "Removed"}

@app.get("/favorites")
def get_favorites():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT c.* FROM cards c
        JOIN favorites f ON c.id = f.id
    """).fetchall()
    conn.close()
    return {"count": len(rows), "results": [dict(r) for r in rows]}
