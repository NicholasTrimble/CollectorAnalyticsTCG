import sqlite3

conn = sqlite3.connect("data/cards.db")
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM cards;")
count = cursor.fetchone()[0]

print(f"Total cards in DB: {count}")

conn.close()
