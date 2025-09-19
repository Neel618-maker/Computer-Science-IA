import sqlite3

def init_db():
    conn = sqlite3.connect("fitness.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )""")

    cursor.execute("""
CREATE TABLE IF NOT EXISTS workout_sets (
    set_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    exercise TEXT,
    reps INTEGER,
    weight_kg REAL,
    is_bodyweight INTEGER DEFAULT 0,
    date TEXT
)""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS goals (
        goal_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        exercise TEXT,
        target_reps INTEGER,
        target_weight REAL,
        deadline TEXT
    )""")
   
    conn.commit()
    conn.close()