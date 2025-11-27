import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.linear_model import LinearRegression
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
def predict_targets(dates, reps, weights):
    if len(dates) < 2:
        return None # Not enough data to make an accurate prediction
    
    days = np.array([(d - dates[0]).days for d in dates]). reshape(-1, 1)
    future_days = np.array([days[-1][0] + i for i in range (1, 6)]).reshape(-1, 1) 
    model_reps = LinearRegression().fit(days, reps)
    model_weight = LinearRegression().fit(days, weights)

    future_reps = model_reps.predict(future_days)
    future_weights = model_weight.predict(future_days)

    # Formula Taken From maths studies
    reps_ci = 1.96 * np.std(reps) / np.sqrt(len(reps))
    weights_ci = 1.96 * np.std(weights) / np.sqrt(len(weights)) 

    return days, future_days, future_reps, future_weights, reps_ci, weights_ci

# actual vs  prediction plot

def plot_predictions(days, reps, weights, future_days, future_reps, future_weights, reps_ci, weights_ci, exercise, student_id):
    plt.figure(figsize=(12, 5))

    # reps plot
    plt.subplot(1, 2, 1)
    plt.plot(days, reps, label = "Actual Reps", marker='o')
    plt.plot(future_days, future_reps, label="predicted Reps", linestyle='--', marker='x')
    plt.fill_between(future_days.flatten(), future_reps - reps_ci, future_reps + reps_ci, color='gray', alpha=0.2, label="95% CI")
    plt.title(f"Reps Prediction for {exercise.capitalize()}")
    plt.xlabel("Days since first workout")
    plt.ylabel("reps")
    plt.legend()

    # weight plot

    plt.subplot(1, 2, 2)
    plt.plot(days, weights, label="Actual Weight", marker='o')
    plt.plot(future_days, future_weights, label="predicted weight", linestyle='--', marker='x')
    plt.fill_between(future_days.flatten(), future_weights - weights_ci, future_weights + weights_ci, color='red', alpha=0.2, label="95% CI")
    plt.title(f"Weight Prediction for {exercise.capitalize()}")
    plt.xlabel("Days since first workout")
    plt.ylabel("weight (Kg)")
    plt.legend()

    plt.tight_layout()
    plt.savefig(f"prediction_{student_id}_{exercise}.png")
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
      except:
          continue
   
    leaderboard.sort(key=lambda x: x[3], reverse=True) 

    return leaderboard[: 10]
    
# Daily leaderboard sanpshot
    
def daily_leaderboard():
        print("daily Leaderboard snapshot")
        show_leaderboard()
        show_leaderboard(exercise_filter="pushups") # example exercise
        show_leaderboard(student_id=123456) # example student id

        schedule.every().day.at("08:00").do(daily_leaderboard)

        if __name__ == "__main__":
            print("Leaderboard scheduler started. Waiting for next run...")
            while True:
                schedule.run_pending()
                time.sleep(60)

              

     




