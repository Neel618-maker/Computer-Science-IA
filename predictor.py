import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.isotonic import IsotonicRegression
import schedule
import time


# Get workout history for a student and exercise
def get_workout_data(student_id, exercise):
    conn = sqlite3.connect("fitness.db")
    cursor = conn.cursor()
    cursor.execute(" SELECT datetime, reps, weight FROM user_workouts WHERE student_id = ? AND exercise = ? ORDER BY datetime ASC ", (student_id, exercise.lower()))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return [], [], []

    dates = [datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S") for row in rows]
    reps =  [row[1] for row in rows]
    weights = [row[2] for row in rows]
    return dates, reps, weights

# predict future reps and weight using linear regression
def predict_targets(dates, reps, weights, user_level="intermediate"):
    if len(dates) < 2:
        return None # Not enough data to make an accurate prediction
    
    days = np.array([(d - dates[0]).days for d in dates]). reshape(-1, 1)
    future_days = np.array([days[-1][0] + i for i in range (1, 6)]).reshape(-1, 1) 

    reps_rate = (reps[-1] - reps[0]) / max((dates[-1] - dates[0]).days, 1)
    weights_rate = (weights[-1] - weights[0]) / max((dates[-1] - dates[0]).days, 1)

    if user_level == "intermediate":
        max_reps, max_weights = 60, 120
    elif user_level == "expert":
        max_reps, max_weights = 100, 170
    else:
        max_reps, max_weights = 60, 120

    if reps[-1] >= 0.9 * max_reps or weights[-1] >= 0.9 * max_weights:
        user_level = "expert"
        max_reps, max_weights = 100, 170

    iso_reps = IsotonicRegression(out_of_bounds='clip')
    iso_reps.fit(days.flatten(), reps)
    iso_pred = iso_reps.predict(future_days.flatten())
    alpha = 0.1
    ceiling_reps = reps[-1] + (max_reps - reps[-1]) * (1 - np.exp(-alpha * np.arange(1, len(future_days)+1)))
    future_reps = np.minimum(ceiling_reps, np.maximum.accumulate(iso_pred))
    future_reps += reps_rate * np.arange(1, len(future_days) + 1)
    
    model_weights = RandomForestRegressor(n_estimators=100, random_state=42).fit(days, weights)
    rf_pred = model_weights.predict(future_days)
    future_weights = weights[-1] + (max_weights - weights[-1]) * (1 - np.exp(-alpha * np.arange(1, len(future_days)+1)))
    ceiling_weights = np.maximum.accumulate(future_weights)
    future_weights = np.minimum(ceiling_weights, np.maximum.accumulate(rf_pred))
    future_weights += weights_rate * np.arange(1, len(future_days) + 1)

    # Formula Taken From maths studies
    reps_ci = 1.96 * np.std(reps) / np.sqrt(len(reps))
    weights_ci = 1.96 * np.std(weights) / np.sqrt(len(weights)) 
    if len(reps) < 5: reps_ci *= 0.5
    if len(weights) < 5: weights_ci *= 0.5

    return days, future_days, future_reps, future_weights, reps_ci, weights_ci

# actual vs  prediction plot

def plot_predictions(days, reps, weights, future_days, future_reps, future_weights, reps_ci, weights_ci, exercise, student_id, user_level="intermediate"):
    plt.figure(figsize=(12, 5))

    # reps plot
    plt.subplot(1, 2, 1)
    plt.plot(days, reps, label = "Actual Reps", marker='o')
    plt.plot(future_days, future_reps, label="predicted Reps", linestyle='--', marker='x')
    lower_reps = np.maximum.accumulate(future_reps - reps_ci)
    upper_reps = future_reps + reps_ci
    plt.fill_between(future_days.flatten(), lower_reps, upper_reps, color='gray', alpha=0.2, label="95% CI")
    plt.title(f"Reps Prediction for {exercise.capitalize()} ({user_level.capitalize()} Level")
    plt.xlabel("Days since first workout")
    plt.ylabel("Reps")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend()

    # weight plot

    plt.subplot(1, 2, 2)
    plt.plot(days, weights, label="Actual Weight", marker='o')
    plt.plot(future_days, future_weights, label="predicted weight", linestyle='--', marker='x')
    lower_weights = np.maximum.accumulate(future_weights - weights_ci)
    upper_weights = future_weights + weights_ci
    plt.fill_between(future_days.flatten(), lower_weights, upper_weights, color='red', alpha=0.2, label="95% CI")
    plt.title(f"Weight Prediction for {exercise.capitalize()} ({user_level.capitalize()} Level)")
    plt.xlabel("Days since first workout")
    plt.ylabel("Weight (Kg)")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend()

    plt.tight_layout()
    plt.savefig(f"prediction_{student_id}_{exercise}_{user_level}.png")
    plt.show()

    # Leaderboard displays

def show_leaderboard(student_id=None, exercise_filter=None):
    conn = sqlite3.connect("fitness.db")
    cursor = conn.cursor()

    query = """
        SELECT u.student_id, u.name, w.exercise, MIN(w.datetime), MAX(w.datetime), MIN(w.reps), MAX(w.reps)
        FROM user_workouts w
        JOIN users u on u.student_id = w.student_id
    """

    filters = []
    params = []

    if student_id is not None:
        filters.append("u.student_id = ?")
        params.append(student_id)
    if exercise_filter is not None:
        filters.append("w.exercise = ?")
        params.append(exercise_filter.lower())

    if filters:
        query += " WHERE " + " AND ".join(filters)

    query += " GROUP BY u.student_id, w.exercise"

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()

    leaderboard = []
 
    for student_id, name, exercise, start_date, end_date, min_reps, max_reps in rows:
      try:
       start = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
       end = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
       days = max((end - start).days, 1)
       rate = (max_reps - min_reps) / days
       leaderboard.append((student_id, name, exercise, round(rate, 2)))
      except ValueError as e:
          print(f"Skipping row due to error: {e}")
          continue
   
    leaderboard.sort(key=lambda x: x[3], reverse=True) 

    return leaderboard[: 10]
    
# Daily leaderboard sanpshot
    
def daily_leaderboard():
        print("daily Leaderboard snapshot")
        print(show_leaderboard())
        print(show_leaderboard(exercise_filter="pushups")) # example exercise
        print(show_leaderboard(student_id=123456)) # example student id

        schedule.every().day.at("08:00").do(daily_leaderboard)

        if __name__ == "__main__":
            print("Leaderboard scheduler started. Waiting for next run...")
            while True:
                schedule.run_pending()
                time.sleep(60)

              

     




