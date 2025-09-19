import sqlite3

# --- Store a goal in the database ---
def set_goal(user_id, exercise, target_reps, target_weight, deadline):
    conn = sqlite3.connect("fitness.db")
    cursor = conn.cursor()

    # Create the goals table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            user_id INTEGER,
            exercise TEXT,
            target_reps INTEGER,
            target_weight REAL,
            deadline TEXT
        )
    """)

    # Insert the goal
    cursor.execute("""
        INSERT INTO goals (user_id, exercise, target_reps, target_weight, deadline)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, exercise, target_reps, target_weight, deadline))

    conn.commit()
    conn.close()

# --- Generate a simple AI progression plan ---
def generate_plan(user_id, exercise):
    conn = sqlite3.connect("fitness.db")
    cursor = conn.cursor()

    # Fetch the latest goal
    cursor.execute("""
        SELECT target_reps, target_weight FROM goals
        WHERE user_id = ? AND exercise = ?
        ORDER BY ROWID DESC LIMIT 1
    """, (user_id, exercise))
    goal_data = cursor.fetchone()

    if not goal_data:
        conn.close()
        return "⚠️ No goal found for this exercise."

    # Safely convert goal values
    try:
        target_reps = int(goal_data[0])
        target_weight = float(goal_data[1])
    except ValueError:
        conn.close()
        return "⚠️ Goal data is invalid."

    # Fetch the latest workout
    cursor.execute("""
        SELECT reps, weight FROM workout_sets
        WHERE user_id = ? AND exercise = ?
        ORDER BY datetime DESC LIMIT 1
    """, (user_id, exercise))
    workout_data = cursor.fetchone()

    conn.close()

    if not workout_data:
        return "⚠️ No workout data found to generate a plan."

    # Safely convert workout values
    try:
        current_reps = int(workout_data[0])
        current_weight = float(workout_data[1])
    except ValueError:
        return "⚠️ Workout data is invalid."

    # Calculate progression steps
    rep_step = max(1, (target_reps - current_reps) // 2)
    weight_step = max(1, (target_weight - current_weight) / 2) if target_weight > 0 else 0

    # Build progression plan
    rep_plan = [current_reps + rep_step * i for i in range(1, 4)]
    weight_plan = [round(current_weight + weight_step * i, 2) if target_weight > 0 else 0 for i in range(1, 4)]

    return {
        "reps": rep_plan,
        "weights": weight_plan
    }
