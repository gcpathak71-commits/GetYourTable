import sqlite3

DB_PATH = "restaurants.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS reservations (
    id TEXT PRIMARY KEY,
    restaurant TEXT NOT NULL,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    people INTEGER NOT NULL,
    cuisine TEXT,
    city TEXT
)
""")

conn.commit()
conn.close()

print("Reservations table created successfully!")
