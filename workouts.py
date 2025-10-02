import sqlite3
from datetime import datetime

# Valid exercises
valid_exercises = ["situps, pushups, squat, deadlift, bench press, leg press, pullups, row, lateral raises, plank, lunge, bicep curl, tricep curl"]
def is_vaild_exercise(exercise):
    return exercise.lower() in valid_exercises

def is_valid_reps(reps):
    return isinstance(reps, int) and reps > 0

def is_valid_weight(weight):
    return isinstance(weight, (int, float)) and weight >= 0

# Add a workout Entry
def add_workout(student_id, exercise, reps, weight, is_bodyweight=False):
    if not is_vaild_exercise(exercise):
        return f"Invalid Exercise : {exercise}"
    if not is_valid_reps(reps):
        return "invalid Reps : must be a positive integer"
    if not is_valid_weight(weight):
        return "Invalid weight: must be a positive number"
    
    timestamp = datetime.now().strftime("%Y-&m-%d %H:%M:%S")

    conn = sqlite3.connect("fitness.db")
    cursor = conn.cursor()
    cursor.execute("""
       INSERT INTO user_workouts (student_id, exercise, reps, weight, datetime, is_bodyweight)
       VALUES (?, ?, ?, ?, ?, ?)
   """, (student_id, exercise.lower(), reps, weight, timestamp, int(is_bodyweight)))
    conn.commit()
    conn.close()
    return "workout added successfully"
                                                                                                                                                               
