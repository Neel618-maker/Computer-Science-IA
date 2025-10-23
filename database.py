import sqlite3

def init_db():
    conn = sqlite3.connect("fitness.db")
    cursor = conn.cursor()

# Raw user and workout log table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_workouts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    


    
    # AI Generated predction table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predicted_targets(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            exercise TEXT NOT NULL,
            predicted_reps INTEGER,
            predicted_weight REAL,
            prediction_date TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)                                                                               


    conn.commit()
    conn.close()    

if __name__ == "__main__":
    init_db()

    # Update records
def update_workout(workout_id, new_reps, new_weight):
    conn = sqlite3.connect("fitness.db")
    cursor = conn.cursor()

    cursor.execute("""
       UPDATE user_workouts
       SET reps = ?, weight = ?
       WHERE id = ?
    """, (new_reps, new_weight, workout_id))
    
    conn.commit()
    conn.close()

    # Delete Records
    
def delete_prediction(prediction_id):
        conn = sqlite3.connect("fitness.db")
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM predicted_targets
            WHERE id = ?
        """, prediction_id, )

        conn.commit()
        conn.close()

        # join records
def join_workouts_and_predictions(student_id):
        conn = sqlite3.connect("fitness.db")
        cursor = conn.cursor

        cursor.execute("""
           SELECT u.datetime, u.exercise, u.reps, u.weight, p.predicted_reps, p.predicted_weight, p.prediction_date
           FROM user_workouts u
           JOIN predicted_targets p
           ON u.student_id = p.student_id AND u.exercise = p.exercise
           WHERE u.student_id = ?
           ORDER BY u.datetime ASC
        """, (student_id))
        
        results = cursor.fetchall()
        conn.close()
        return results
# execute the join functon
join_workouts_and_predictions(123456)


