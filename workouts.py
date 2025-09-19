import sqlite3
def log_workout(user_id, exercise, reps, weight, is_bodyweight, datetime):
    conn = sqlite3.connect("fitness.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workout_sets (
            user_id INTEGER,
            exercise TEXT,
            reps INTEGER,
            weight REAL,
            is_bodyweight INTEGER,
            datetime TEXT
        )
    """)

    cursor.execute("""
        INSERT INTO workout_sets (user_id, exercise, reps, weight, is_bodyweight, datetime)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, exercise, reps, weight, is_bodyweight, datetime))

    conn.commit()
    conn.close()

