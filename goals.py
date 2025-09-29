import sqlite3

def set_goal(user_id, exercise, target_reps, target_weight):
    # valdate limits
    if not (1 <= target_reps <= 500):
        raise ValueError("target_reps must be between 1 and 500")
    if not (0 <= target_weight <= 500):
        raise ValueError("target_weight must be between 0 and 500")
    conn = sqlite3.connect("fitness.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO goals (user_id, exercise, target_reps, traget_weight)
        VALUES (?, ?, ?, ?) 
    """, (user_id, exercise, target_reps, target_weight))
    conn.commit()
    conn.close()
    print(" goal set successfully.")


