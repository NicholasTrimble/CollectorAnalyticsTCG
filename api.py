from fastapi import FastAPI, Query
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


@app.get("/cards")
def read_cards(
    rarity: str | None = Query(default=None),
    sort: str | None = Query(default=None),
    order: str | None = Query(default="asc"),
    search: str | None = Query(default=None)
):
    results = query_cards(rarity, sort, order, search)
    return {"count": len(results), "results": results}
