import sqlite3

def init_db():
    conn = sqlite3.connect("fitness.db")
    cursor = conn.cursor()

# Raw user and workout log table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_workouts(
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,))
        name TEXT NOT NULL,
        house TEXT NOT NULL,
        student_id INTEGER NOT NULL UNIQUE,
        password TEXT NOT NULL,
        exercise TEXT NOT NULL,
        reps INTEGER NOT NULL,
        weight REAL NOT NULL,
        is_bodyweight INTEGER NOT NULL,
        datetime TEXT DEFAULT CURRENT_TIMESTAMP
   ) 
""")

# RAW goals table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user goals(
        goal_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        exercise TEXT NOT NULL,
        target reps INTEGER NOT NULL,
        target weight REAL NOT NULL,
        datetime TEXT DEFAULT CURRENT_TIMESTAMP
    )
 """)
    conn.commit()
    conn.close()    