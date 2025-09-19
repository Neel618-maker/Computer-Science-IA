from workouts import log_workout
from goals import set_goal
from database import init_db
from datetime import datetime

# --- Step 1: Initialize the database ---1
init_db()

# --- Step 2: Set default user ID ---
user_id = 1

# --- Step 3: Log a workout ---
print("👋 Welcome to your AI Workout Planner!")
print("Let's start by logging your workout.\n")

exercise = input("🏋️ Enter exercise you would like to focus on: ")
reps = int(input("🔢 Enter number of reps you can do currently: "))
weight = float(input("⚖️ Enter weight in kg you can do currently(0 for bodyweight): "))
is_bodyweight = weight == 0
timestamp = datetime.now().isoformat()

log_workout(user_id, exercise, reps, weight, is_bodyweight, timestamp)
print(f"\n✅ Logged: {reps} reps of {exercise} at {weight}kg on {timestamp[:10]}.")

# --- Step 4: Set a goal ---
print("\n🎯 Now let's set your goal.\n")

target_reps = int(input("🔢 Enter target reps: "))
while True:
    try:
        target_weight = float(input("⚖️ Enter target weight in kg: "))
        break
    except ValueError:
        print ("❌ That doesn't look like a number. Please enter a weight in kg (e.g. 50.0).")
deadline = input("📅 Enter deadline (YYYY-MM-DD): ")

set_goal(user_id, exercise, target_reps, target_weight, deadline)
print(f"\n🎯 Goal set for {exercise}: {target_reps} reps @ {target_weight}kg by {deadline}.")

# --- Step 5: Generate time-aware AI plan ---
print("\n🤖 Generating your AI progression plan...\n")

# Calculate time until deadline
deadline_date = datetime.strptime(deadline, "%Y-%m-%d")
today = datetime.now()
total_days = (deadline_date - today).days
total_weeks = max(1, total_days // 7)

# Calculate progression steps
rep_step = max(1, (target_reps - reps) // total_weeks)
weight_step = (target_weight - weight) / total_weeks if target_weight > 0 else 0

# Build and display plan
print("📅 Your Week-by-Week Plan:")
for week in range(1, total_weeks + 1):
    projected_reps = reps + rep_step * week
    projected_weight = round(weight + weight_step * week, 2) if not is_bodyweight else 0
    print(f"Week {week}: {projected_reps} reps @ {projected_weight}kg")
print("Good luck!")
import sqlite3
import matplotlib.pyplot as plt

def plot_progress(user_id, exercise):
    conn = sqlite3.connect("fitness.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT datetime, reps, weight FROM workout_sets
        WHERE user_id = ? AND exercise = ?
        ORDER BY datetime ASC
    """, (user_id, exercise))

    data = cursor.fetchall()
    conn.close()

    if not data:
        print("⚠️ No workout data found to plot.")
        return

    dates = [row[0][:10] for row in data]  # Just the date part
    reps = [row[1] for row in data]
    weights = [row[2] for row in data]

    # --- Plotting ---
    plt.figure(figsize=(10, 5))
    plt.plot(dates, reps, label="Reps", marker='o')
    plt.plot(dates, weights, label="Weight (kg)", marker='s')
    plt.xticks(rotation=45)
    plt.xlabel("Date")
    plt.ylabel("Performance")
    plt.title(f"Progress for {exercise}")
    plt.legend()
    plt.tight_layout()
    plt.show()
 
