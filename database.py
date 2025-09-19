import sqlite3

def init_db():
    conn = sqlite3.connect("fitness.db")
    cursor = conn.cursor()

    cursor.execute('''
      CREATE TABLE IF NOT EXISTS users(
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
        house TEXT
        student_id TEXT UNIQUE
        password TEXT NOT NULL
        exercise_id TEXT,
        created_at TEXT DEFAULT CURRENT TIMESTAMP
    )
    ''')    
    
    cursor.execute('''
      CREATE TABLE IF NOT EXISTS workout_sets(
        user_id INTEGER,
        exerciese TEXT,
        reps INTEGER,
        weight REAL
        is_bodyweight INTEGER,
        datetime TEXT DEFAULT CURRENT TIMESTAMP,
    )                                                                                                                                   
 ''')
    
    cursor.execute(''')
      CREATE TABLE IF NOT EXISTS goals(
        user_id INTEGER,
        exercise TEXT,  
        target_reps INTEGER
        target_weight REAL,
    )
 ''')

    conn.commit()
    conn.close()
    def add_user(name, house, student_id, password):
        conn = sqlite3.connect("fitness.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO users (name, house, student_id, password)
                Values (?, ?, ?, ?)
                       """, (name, house, student_id, password))