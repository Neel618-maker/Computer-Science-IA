import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
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
   # Polynomial Regression Algorithm
def polynomial_regression(x_values, y_values, degree=2):
    # First step is to create the design matrix where each row 
    # corresponds to a power of x (days since first workout)
    # works out exact numbers for the curve to match the data closely
    X = [[x**i for i in range(degree+1)]for x in x_values]
    XT = list(map(list, zip(*X))) # swap rows and columns in matrix X
    XT_X = [[sum(a*b for a, b in zip(row, col))for col in zip(*X)] for row in XT]
    # The code above just multiplies matrix XT with matrix X
    XT_y = [sum(a*b for a, b in zip(row, y_values)) for row in XT]
    # The code above multiplies matrix XT with vector y_values
    coeffs = gaussian_elimination(XT_X, XT_y)
    return coeffs

# Solve equations using the Gaussian elimination model
# Performs forward elimination and back substitution 
# Solves system of equations

def gaussian_elimination(A, b):
    n = len(A)
    # Forward elimination to reduce matrix to upper triangular form
    for i in range(n):
        pivot = A[i][i]
        for J in range(i, n):
            A[i][J] /= pivot
            b[i] /=pivot
            for k in range (i+1, n):
                factor = A[k][i]
                for J in range(i, n):
                    A[k][J] -= factor * A[i][J]
                b[k] -= factor * b[i]
    # Back substitutiion to solvefor each coefficient
    # Starts from the bottom row and works upwards
    x = [0]*n
    for i in range(n-1, -1, -1):
        x[i] = b[i] - sum(A[i][J] * x[J] for J in range (i+1, n))
    return x




# predict future reps and weight using Polynomial regression and user level implementation
def predict_targets(dates, reps, weights, user_level="intermediate", degree=2):
    if len(dates) < 2: # If less than 2 workouts are logged
        return None # Not enough data to make an accurate prediction
    # This function allowws dates to be converted into days since first workout
    days = np.array([(d - dates[0]).days for d in dates])
    future_days = np.arange(days[-1] + 1, days[-1] + 6)
    #  +6 to predict the next 5 days weekly predictions
    # Polynomial REGRESSION FOR Reps
   
    if user_level == "intermediate":
        max_reps, max_weights = 60, 20
    elif user_level == "expert":
        max_reps, max_weights = 100, 70
    else:
        max_reps, max_weights = 60, 20

    if reps[-1] >= 0.9 * max_reps or weights[-1] >= 0.9 * max_weights:
        user_level = "expert"
        max_reps, max_weights = 100, 70

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

    return days, future_days, future_reps, future_weights, reps_ci, weights_ci, user_level

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
    plt.title(f"Reps Prediction for {exercise.capitalize()} ({user_level.capitalize()} Level)")
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

    return future_days, future_reps, future_weights, reps_ci, weights_ci

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

              

     




