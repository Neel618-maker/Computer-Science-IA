from workouts import log_workout
from goals import set_goal, generate_plan
from database import init_db

# Initialize database
init_db()

# Default user ID (can be dynamic later)
user_id = 1

# --- Step 1: Input Workout ---
exercise = input("Enter exercise name: ")
reps = int(input("Enter number of reps: "))
weight = float(input("Enter weight in kg (0 for bodyweight): "))
is_bodyweight = weight == 0

log_workout(user_id, exercise, reps, weight, is_bodyweight)
print(f"✅ Logged: {reps} reps of {exercise} at {weight}kg.")

# --- Step 2: Set Goal ---
target_reps = int(input("Enter target reps: "))
target_weight = float(input("Enter target weight in kg: "))
deadline = input("Enter deadline (YYYY-MM-DD): ")

set_goal(user_id, exercise, target_reps, target_weight, deadline)
print(f"🎯 Goal set for {exercise}: {target_reps} reps @ {target_weight}kg by {deadline}")

# --- Step 3: Generate AI Plan ---
plan = generate_plan(user_id, exercise)
print("🤖 Your AI Plan:")
print(plan)
