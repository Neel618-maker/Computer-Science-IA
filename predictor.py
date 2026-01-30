import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import schedule
import time

# --- HELPER: BIOLOGY MATH ---
def calculate_e1rm(weight, reps):
    """
    Calculates Estimated 1 Rep Max (Strength Score).
    Formula: Weight * (1 + Reps/30)
    This allows us to compare 100kg x 1 vs 85kg x 5 fairly.
    """
    if reps < 1: return 0
    if reps == 1: return weight
    return weight * (1 + (reps / 30.0))

# --- DATABASE HANDLER ---
def get_workout_data(student_id, exercise):
    conn = sqlite3.connect("fitness.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT datetime, reps, weight 
        FROM user_workouts 
        WHERE student_id = ? AND exercise = ? 
        ORDER BY datetime ASC 
    """, (student_id, exercise.lower()))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return [], [], [], []

    dates = [datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S") for row in rows]
    reps = np.array([row[1] for row in rows])
    weights = np.array([row[2] for row in rows])

    # Calculate Strength Score (e1RM) for every workout
    e1rms = []
    for r, w in zip(reps, weights):
        # If it's a bodyweight exercise with 0 weight, track reps only
        if w == 0 or w is None:
            e1rms.append(r)
        else:
            e1rms.append(calculate_e1rm(w, r))

    return dates, reps, weights, np.array(e1rms)

# --- REALISTIC PREDICTION ENGINE ---
def predict_realistic(dates, e1rms, exercise_name="bench press", user_level="intermediate"):
    if len(dates) < 2:
        return None 

    # 1. Convert dates to "Days Since Start"
    days = np.array([(d - dates[0]).days for d in dates])
    
    # 2. Define Future (Next 7 Days)
    last_day = days[-1]
    future_days = np.arange(last_day + 1, last_day + 8)

    # 3. LINEAR REGRESSION (Replacing Gaussian Elimination)
    # Degree 1 = Straight Line. This is safer for fitness predictions.
    slope, intercept = np.polyfit(days, e1rms, 1)
    
    # Calculate the raw prediction line
    future_strength = slope * future_days + intercept

    # 4. REALISM CLAMP (The "Safety Governor")
    # Even if the math predicts huge gains, we cap growth at 2.5% per week
    current_strength = e1rms[-1]
    max_safe_strength = current_strength * 1.025 # Max 2.5% gain
    
    # Apply the clamp
    if slope > 0:
        # If improving, cap at safe limit
        future_strength = np.clip(future_strength, current_strength, max_safe_strength)
    else:
        # If regressing, don't let it crash to zero (assume 5% floor variance)
        future_strength = np.maximum(future_strength, current_strength * 0.95)

    # 5. CONVERT BACK TO REPS/WEIGHT ADVICE
    # We convert the abstract "Strength Score" back into a weight recommendation for 8 reps
    suggested_weights = []
    is_bodyweight = exercise_name.lower() in ["pushups", "situps", "pullups", "plank", "lunge"]
    
    for s in future_strength:
        if is_bodyweight:
            # For bodyweight, the 'strength' is just the rep count
            suggested_weights.append(int(s))
        else:
            # Reverse Formula: Weight = Strength / (1 + 8/30)
            # We suggest 8 reps as a standard hypertrophy range
            w_for_8_reps = s / (1 + (8 / 30.0))
            suggested_weights.append(round(w_for_8_reps, 1))

    return days, future_days, future_strength, suggested_weights

# --- PLOTTING ---
def plot_predictions(days, e1rms, future_days, future_strength, exercise, student_id):
    plt.figure(figsize=(10, 6))
    
    # Plot History
    plt.scatter(days, e1rms, color='blue', label='Actual History')
    
    # Plot Prediction
    plt.plot(future_days, future_strength, color='green', linestyle='--', marker='x', label='Projected Safe Growth')
    
    # Formatting
    plt.title(f"Progress Projection: {exercise.capitalize()}")
    plt.xlabel("Days Since First Workout")
    plt.ylabel("Strength Index (Est. 1 Rep Max or Reps)")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    
    # Save and Show
    filename = f"pred_{student_id}_{exercise}.png"
    plt.savefig(filename)
    plt.show()
    print(f"Graph saved as {filename}")

# --- LEADERBOARD (Kept mostly the same) ---
def show_leaderboard():
    conn = sqlite3.connect("fitness.db")
    cursor = conn.cursor()
    # Calculates improvement based on max strength achieved vs initial strength
    query = """
        SELECT u.name, w.exercise, MIN(w.datetime), MAX(w.datetime), MIN(w.reps), MAX(w.reps), MIN(w.weight), MAX(w.weight)
        FROM user_workouts w
        JOIN users u on u.student_id = w.student_id
        GROUP BY u.student_id, w.exercise
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    
    leaderboard = []
    for name, exercise, start, end, min_r, max_r, min_w, max_w in rows:
        try:
            # Calculate simple strength delta
            start_str = calculate_e1rm(min_w, min_r)
            end_str = calculate_e1rm(max_w, max_r)
            
            # Improvement %
            if start_str > 0:
                imp = ((end_str - start_str) / start_str) * 100
                leaderboard.append((name, exercise, round(imp, 1)))
        except:
            continue
            
    leaderboard.sort(key=lambda x: x[2], reverse=True)
    return leaderboard[:10]

# --- MAIN EXECUTION BLOCK ---
if __name__ == "__main__":
    # Example usage (simulating a run)
    print("--- Fitness Tracker Prediction ---")
    
    # 1. Mock Data (Replace with inputs in real app)
    s_id = 123
    ex_name = "bench press"
    
    # Note: In a real app, you'd ensure the DB has data first.
    # For this demo, we assume the DB handles the inputs.
    try:
        dates, reps, weights, e1rms = get_workout_data(s_id, ex_name)
        
        if len(dates) > 1:
            days, f_days, f_str, advice = predict_realistic(dates, e1rms, ex_name)
            
            print(f"\nPrediction for {ex_name}:")
            for i, day in enumerate(f_days):
                print(f"  Day {day}: Target Strength {f_str[i]:.1f} -> Try {advice[i]} kg for 8 reps")
            
            plot_predictions(days, e1rms, f_days, f_str, ex_name, s_id)
        else:
            print("Not enough data to predict yet. Log at least 2 workouts!")
            
    except Exception as e:
        print(f"Error (likely no DB found): {e}")


     




