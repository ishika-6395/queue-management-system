import sqlite3
import os

# Database file ka naam
DB_NAME = "queue_system.db"

# Purana database delete karein agar exist karta hai
if os.path.exists(DB_NAME):
    os.remove(DB_NAME)
    print("🗑 Old database deleted.")

# Naya database create karein
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Users table create karein
cursor.execute("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        is_admin INTEGER DEFAULT 0
    )
""")

# Bookings table create karein
cursor.execute("""
    CREATE TABLE bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        service_type TEXT NOT NULL CHECK(service_type IN ('Bank', 'Hospital')),
        date TEXT NOT NULL,  -- YYYY-MM-DD format
        time TEXT NOT NULL,  -- HH:MM (24-hour format)
        token_number INTEGER NOT NULL
    )
""")

# Changes commit karein aur connection close karein
conn.commit()
conn.close()

print("✅ New database created successfully with required tables!")