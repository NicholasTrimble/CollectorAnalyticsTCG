import sqlite3

DB_File = "data/cards.db"

conn = sqlite3.connect(DB_File)
cursor = conn.cursor()

cursor.execute("""
Create Table If Not Exists favorites (
    id TEXT Primary Key,
               added_at Text Default CURRENT_TIMESTAMP
);
""")
conn.commit()
conn.close()

print("Favorites table ready.")
