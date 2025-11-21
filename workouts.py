import sqlite3
from datetime import datetime

# Valid exercises
valid_exercises = ["situps" , "pushups", "squat", "deadlift", "bench press", "leg press", "pullups", "row", "lateral raises", "plank", "lunge", "bicep curl", "tricep curl"]
def is_valid_exercise(exercise):
    return exercise.lower() in valid_exercises

def is_valid_reps(reps):
    return isinstance(reps, int) and reps > 0

def is_valid_weight(weight):
    return isinstance(weight, (int, float)) and weight >= 0

# Add a workout Entry
def add_workout(student_id, exercise, reps, weight, is_bodyweight=False):
    if not is_valid_exercise(exercise):
        return f"Invalid Exercise : {exercise}"
    if not is_valid_reps(reps):
        return "invalid Reps : must be a positive integer"
    if not is_valid_weight(weight):
        return "Invalid weight: must be a positive number"
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect("fitness.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO user_workouts (student_id, exercise, reps, weight, datetime, is_bodyweight) VALUES (?, ?, ?, ?, ?, ?)", (student_id, exercise.lower(), reps, weight, timestamp, int(is_bodyweight)))
    conn.commit()
    conn.close()
    return "workout added successfully"

def get_workouts(student_id):
    conn = sqlite3.connect("fitness.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, exercise, reps, weight, datetime, is_bodyweight FROM user_workouts WHERE student_id = ? ORDER BY datetime Asc", (student_id))   

    results = cursor.fetchall()
    conn.close()
    return results

# update workout entry
def update_workout(workout_id, exercise, reps, weight, is_bodyweight):
    if not is_valid_exercise(exercise):
        return f"Invalid exercise: {exercise}"
    if not is_valid_reps(reps):
        return "Invalid reps: must be a positive integer"
    if not is_valid_weight(weight):
        return "Invalid weight: must be a positive number"
    
    conn = sqlite3.connect("fitness.db")
    cursor = conn.cursor()
    cursor.execute(""" SELECT 1 FROM user_workouts WHERE id = ?""", (workout_id))
    if not cursor.fetchone():
        conn.close()
        return " No workout found with ID {workout_id}"
    
    cursor.execute("UPDATE user_workouts SET exercise = ?, reps = ?, weight = ?, is_bodyweight = ? WHERE id = ?", (exercise.lower(), reps, weight, int(is_bodyweight), workout_id))
    conn.commit()
    conn.close()
    return "workout updated successfully"

# Delete workout entry
def delete_workout(workout_id):
    conn = sqlite3.connect("fitness.db")
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM user_workouts WHERE id = ?", (workout_id))
    if not cursor.fetchone():
        conn.close()
        return f"No workout found with ID {workout_id}"
    
    cursor.execute("DELETE FROM user_workouts WHERE id = ?", (workout_id))
    conn.commit()
    conn.close()
    return "workout entrry {workout_id} deleted successfully"

# retrieve workouts for a user
def get_workouts(student_id, exercise):
    conn = sqlite3.connect("fitness.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, exercise, reps, weight, datetime, is_bodyweight FROM user_workouts WHERE student_id = ? AND exercise = ? ORDER BY datetime ASC", (student_id, exercise.lower()))
    results = cursor.fetchall()
    conn.close()
    return results



    




                                                                                                                                                               
