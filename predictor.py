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
        pivot = A[i][i] # diagonal element used to eliminate below
        # Scale the pivot row so pivot becomes 1
        for J in range(i, n): 
            A[i][J] /= pivot
        b[i] /=pivot
            # Eliminate the current variable from all rows below
        for k in range (i+1, n):
            factor = A[k][i]
            for J in range(i, n):
                A[k][J] -= factor * A[i][J]
            b[k] -= factor * b[i]
    # Back substitutiion to solvefor each coefficient
    # Starts from the bottom row and works upwards
    x = [0]*n
    for i in range(n-1, -1, -1):
        # Each row now has fewer variables to solve for
        x[i] = b[i] - sum(A[i][J] * x[J] for J in range (i+1, n))
    return x

# Predicts the new values using polynomial coefficients
# Given the coefficients and x value 
# Calculates y = a0 + a1*x + a2*x^2 + ...
def predict(coeffs, x):
    return sum(coeffs[i] * (x**i) for i in range(len(coeffs)))





# predict future reps and weight using Polynomial regression and user level implementation
# Configures user level based on performance
def predict_targets(dates, reps, weights=None, degree=3):
    if len(dates) < 2:
        return None

    days = np.array([(d - dates[0]).days for d in dates])
    future_days = np.arange(days[-1] + 1, days[-1] + 6)

    # Polynomial fit for reps
    reps_coeffs = polynomial_regression(days, reps, degree=degree)
    future_reps = np.array([predict(reps_coeffs, d) for d in future_days], dtype=float)
    residuals = reps - np.array([predict(reps_coeffs, d) for d in days])
    reps_ci = max(1.96 * np.std(residuals), 2)  # enforce minimum CI
    last_reps = reps[-1]
    future_reps = np.clip(future_reps, last_reps, last_reps * 2)

    # Polynomial fit for weights (if available)
    future_weights, weights_ci = None, None
    if weights is not None and len(weights) > 1:
        weights_coeffs = polynomial_regression(days, weights, degree=2)
        future_weights = np.array([predict(weights_coeffs, d) for d in future_days], dtype=float)
        weights_residuals = weights - np.array([predict(weights_coeffs, d) for d in days])
        weights_ci = max(1.96 * np.std(weights_residuals), 2)
        last_weights = weights[-1]
        future_weights = np.clip(future_weights, last_weights, last_weights * 2)

    return days, future_days, future_reps, future_weights, reps_ci, weights_ci

def plot_predictions(days, reps, weights, future_days, future_reps, future_weights, reps_ci, weights_ci, exercise):
    plt.figure(figsize=(12, 5))

    # Reps plot
    plt.subplot(1, 2, 1)
    plt.plot(days, reps, 'o-', label="Actual Reps")
    plt.plot(future_days, future_reps, 'x--', label="Predicted Reps")
    plt.fill_between(future_days, future_reps - reps_ci, future_reps + reps_ci,
                     color='gray', alpha=0.3, label="95% CI")
    plt.title(f"{exercise.capitalize()} Reps Prediction")
    plt.xlabel("Days since first workout")
    plt.ylabel("Reps")
    plt.legend()
    plt.grid(True)

    # Weights plot (if available)
    if future_weights is not None and weights is not None:
        plt.subplot(1, 2, 2)
        plt.plot(days, weights, 'o-', label="Actual Weights")
        plt.plot(future_days, future_weights, 'x--', label="Predicted Weights")
        plt.fill_between(future_days, future_weights - weights_ci, future_weights + weights_ci,
                         color='red', alpha=0.3, label="95% CI")
        plt.title(f"{exercise.capitalize()} Weight Prediction")
        plt.xlabel("Days since first workout")
        plt.ylabel("Weight (kg)")
        plt.legend()
        plt.grid(True)

    plt.tight_layout()
    plt.show()



def show_leaderboard(student_id=None, exercise_filter=None):
    conn = sqlite3.connect("fitness.db") # connect to the database 
    cursor = conn.cursor()

    query = """
        SELECT u.student_id, u.name, w.exercise, MIN(w.datetime), MAX(w.datetime), MIN(w.reps), MAX(w.reps)
        FROM user_workouts w
        JOIN users u on u.student_id = w.student_id
    """
    # query to collect user's exercise history from database for leaderboard calculations
    filters = []
    params = []

    if student_id is not None:
        filters.append("u.student_id = ?") # allows user to filter by student_id
        params.append(student_id) # stores the student id value
    if exercise_filter is not None: 
        filters.append("w.exercise = ?") # allows user to filter by exercise
        params.append(exercise_filter.lower()) # stores exercise name in lower case
# If any more filters exist join them to the query using WHERE and AND
    if filters:
        query += " WHERE " + " AND ".join(filters)
 # groups results by student and exercise to calculate the improvement per exercise
    query += " GROUP BY u.student_id, w.exercise"
# execute the querry with the parameters and fetch all matching rows
    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()

    leaderboard = []
 # Process each row to calculate improvement rate
    for student_id, name, exercise, start_date, end_date, min_reps, max_reps in rows:
      try:
       # Convert dates into datetime 
       start = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
       end = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
      # Calculate days between first and latest workout logged (also avoids division by 0)
       days = max((end - start).days, 1)
      # Improvement rate calculation
       rate = (max_reps - min_reps) / days
      # Add updated student info and improvement rate for the exercise on the leaderboard
       leaderboard.append((student_id, name, exercise, round(rate, 2)))
      except ValueError as e:
    # Skips row if there's an error in date conversion
          print(f"Skipping row due to error: {e}")
          continue
   # sorts leaderboard with highest improvement rate being first
    leaderboard.sort(key=lambda x: x[3], reverse=True) 

    return leaderboard[: 10]
    
# Daily leaderboard sanpshot
    
def daily_leaderboard():
        print("daily Leaderboard snapshot")
        # Shows the leaderboard
        print(show_leaderboard())
        print(show_leaderboard(exercise_filter="pushups")) # example exercise
        print(show_leaderboard(student_id=123456)) # example student id

        schedule.every().day.at("08:00").do(daily_leaderboard)

        if __name__ == "__main__":
            print("Leaderboard scheduler started. Waiting for next run...")
            while True:
                schedule.run_pending()
                time.sleep(60) # waits a minute before checking again

              

     




