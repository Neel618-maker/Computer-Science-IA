import sqlite3

def init_db():
    conn = sqlite3.connect("fitness.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        password TEXT NOT NULL
     )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_workouts (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           student_id INTEGER NOT NULL,                          
           exercise TEXT NOT NULL,
           reps INTEGER NOT NULL,
           weight REAL NOT NULL,
           is_bodyweight INTEGER NOT NULL,
           datetime TEXT DEFAULT CURRENT_TIMESTAMP,
           FOREIGN KEY (student_id) REFERENCES users(student_id) ON DELETE CASCADE
        )                                                   
    """)

    conn.commit()
    conn.close()

    # USER functions
def is_student_id_taken(student_id: int) -> bool:
        conn = sqlite3.connect("fitness.db")
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE student_id = ?", (student_id,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists

def register_user(student_id: int, name: str, password: str):
      conn = sqlite3.connect("fitness.db")
      cursor = conn.cursor()
      cursor.execute("INSERT INTO users (student_id, name, password) VALUES (?, ?, ?)", (student_id, name, password,))
      conn.commit()
      conn.close()

# WORKOUT functions
def add_workout(student_id: int, exercise: str, reps: int, weight: float, is_bodyweight: int):
      conn = sqlite3.connect("fitness.db")
      cursor = conn.cursor()
      cursor.execute("INSERT INTO user_workouts (student_id, exercise, reps, weight, is_bodyweight) VALUES (?, ?, ?, ?, ?)", (student_id, exercise, reps, weight, is_bodyweight,))
      conn.commit()
      conn.close()

def get_exercise_list(student_id: int):
      conn = sqlite3.connect("fitness.db")
      cursor = conn.cursor()
      cursor.execute("SELECT DISTINCT exercise FROM user_workouts WHERE student_id = ?", (student_id,))
      exercises = [row[0] for row in cursor.fetchall()]
      conn.close()
      return exercises

def get_workout_data(student_id: int, exercise: str):
      conn = sqlite3.connect("fitness.db")
      cursor = conn.cursor()
      cursor.execute("SELECT datetime, reps, weight FROM user_workouts WHERE student_id = ? AND exercise = ? ORDER BY datetime ASC", (student_id, exercise,))
      rows = cursor.fetchall()
      conn.close()

      dates = [row[0] for row in rows]
      reps = [row[1] for row in rows]
      weights = [row[2] for row in rows]
      return dates, reps, weights

def get_workout_history(student_id: int):
      conn = sqlite3.connect("fitness.db")
      cursor = conn.cursor()
      cursor.execute("SELECT id, datetime, exercise, reps, weight, is_bodyweight FROM user_workouts WHERE student_id = ? ORDER BY datetime DESC", (student_id,))
      rows = cursor.fetchall()
      conn.close()
      return rows

def delete_workout(workout_id: int):
      conn = sqlite3.connect("fitness.db")
      cursor = conn.cursor()
      cursor.execute("DELETE FROM user_workouts WHERE id = ?", (workout_id,))
      conn.commit()
      conn.close()

init_db()


import sqlite3

conn = sqlite3.connect("fitness.db")
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(tables)



