from database import init_db
from auth0 import register, login
from workouts import log_workout
from goals import generate_plan, set_goal
from summary import generate_summary
from utils import calculate_progress

init_db()

# Register and login hello
register("neel@example.com", "securepass123")
user_id = login("neel@example.com", "securepass123")

if user_id:
    print("✅ Login successful!")

    # Log workout
    log_workout(user_id, "Bicep Curl", 6, 10)
    print("✅ Workout logged.")

    # Set goal
    set_goal(user_id, "Bicep Curl", 10, 15, "2025-12-01")
    print("✅ Goal set.")

    # Generate plan
    plan = generate_plan(10, 15)
    print("📈 AI Plan:", plan)

    # Show summary
    generate_summary(user_id, "Bicep Curl")

    # Show progress
    progress = calculate_progress(10, 15)
    print(f"🎯 Progress: {progress}%")
else:
    print("❌ Login failed.")