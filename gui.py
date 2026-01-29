
# Create GUI window Main page for application
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime
import pytz
from workouts import add_workout, get_workouts
from predictor import (get_workout_data, predict_targets, plot_predictions, show_leaderboard)

conn = sqlite3.connect("fitness.db")
conn.execute("PRAGMA foreign_keys = ON")
cursor = conn.cursor()
#Leaderboard window
# sets up the leaderboard table based on whether global or personal mode is selected
def update_leaderboard(table, data, mode="global"):
    table.delete(*table.get_children())
    if mode == "personal": # personal leaderboard
        table["columns"] = ("col1", "col2", "col3") # sets up 3 columns
        table.heading("col1", text="Rank") # first column is rank
        table.heading("col2", text="Exercise") # second column is exercis
        table.heading("col3", text="Rate (Reps/Day)") # third is rate
        # student_id not required here as only one user is being compared
        # ranks the exercise based on rate
        for rank, (exercise, rate) in enumerate(data, start=1):
            # inserts data into the table
            table.insert("", "end", values=(rank, exercise, f"{rate:.2f}"))

    else:
        if mode == "global": # global leaderboard
         table["columns"] = ("col1", "col2", "col3", "col4", "col5") # 5 columns
         table.heading("col1", text="Rank")
         table.heading("col2", text="student_id") # shows users who is being shown on the leaderboard
         table.heading("col3", text="Name") # column for name
         table.heading("col4", text="Exercise")
         table.heading("col5", text="Rate (Reps/Day)")
        for rank, row in enumerate(data, start=1):
            student_id, name, exercise, rate = row
            try:
                rate_val = float(rate)
                rate_fmt = f"{rate_val:.2f}"
            except (ValueError, TypeError):
                rate_fmt = str(rate)
            # inserts data into the table
            table.insert("", "end", values=(rank, student_id, name, exercise, rate_fmt))
        # Shows the global leaderboard as a table
def show_global_leaderboard(table):
    try:
        data = show_leaderboard()
        update_leaderboard(table, data, mode="global")
    except Exception as e:
        messagebox.showerror("Error", str(e))
# shows the personal leaderboard
def show_personal_leaderboard(table, student_id):
    try:
        raw_data = show_leaderboard(student_id=student_id)
        personal_data = [(exercise, rate) for _, _, exercise, rate in raw_data]
        # updates the leaderboard table
        update_leaderboard(table, personal_data, mode="personal")
    except Exception as e:
        messagebox.showerror("Error", str(e))
# Predictions
def show_predictions(student_id, exercise_entry, level_label, table_widget):
    # for the predictions tab shows predicted reps and weights for a specific exercise
    exercise = exercise_entry.get().strip().lower()
    if not exercise: # ensures user enters an exercis
        messagebox.showerror("Input Error", "Please enter an exercise name.")
        return
    try:
        dates, reps, weights = get_workout_data(student_id, exercise)

        if not dates:
            messagebox.showerror("Data Error", f"No workout data found for exercise: {exercise}, inaccurate date.")
            return
        result = predict_targets(dates, reps, weights)
        if result:
            days, future_days, future_reps, future_weights, reps_ci, weights_ci, user_level = result
            # generates and displays the prediction plot
            plot_predictions(days, reps, weights, future_days, future_reps, future_weights, reps_ci, weights_ci, exercise, student_id, user_level)
            # ensures that the user level is visible and the text is green unless user hits expert where it's gold 
            level_label.config(text=f"Current Level: {user_level.capitalize()}", fg="gold" if user_level == "expert" else "green")
            if user_level == "expert":
                # When user reaches expert level they get a congratulations message
                messagebox.showinfo("Level Up!", f"congratulations based on your progress in {exercise}, you have reached expert level!")
            else:
                messagebox.showinfo("Prediction Complete", f"Prediction plot generated for {exercise}.")
            table_widget.delete(*table_widget.get_children())
            for i in range(len(future_days)):
                # inesrts the predicted data into the table directly in the predictions tba
                table_widget.insert("", "end", values=(int(future_days[i]), int(round(future_reps[i])), round(future_weights[i], 1), f"± {int(round(reps_ci))}", f"± {round(weights_ci, 1)}" ))    
        else:
            messagebox.showinfo("Insufficient Data to make a strong prediction")
    except Exception as e:
        messagebox.showerror("Error", str(e))
# Workouts
def add_workout(student_id, exercise, reps, weight, is_bodyweight, timestamp):
    try:
        with sqlite3.connect("fitness.db") as conn: # Connects to the database
          cursor = conn.cursor() # creates a cursor object to execute the SQl commands
          cursor.execute("INSERT INTO user_workouts (student_id, datetime, exercise, reps, weight, is_bodyweight) VALUES (?, ?, ?, ?, ?, ?)", (student_id, timestamp, exercise, reps, weight, is_bodyweight,))
          conn.commit() # commits the changes to the database
          
    except Exception as e:
        messagebox.showerror("Database Error", str(e))

def get_workouts(student_id):
    try:
        conn = sqlite3.connect("fitness.db")
        cursor = conn.cursor()
        # makes sure that the data is fetched in the chronological order of workout date
        cursor.execute("SELECT id, datetime, exercise, reps, weight, is_bodyweight FROM user_workouts WHERE student_id=? ORDER BY datetime", (student_id,))
        return cursor.fetchall()
    except Exception as e: # catches any datase errors
        messagebox.showerror("Database Error", str(e)) 
        return []
    

def get_exercise_list(student_id):
    try:
        # Fetches all unique exercises for the dropdown menu
        workouts = get_workouts(student_id)
        exercises = sorted(set([w[2] for w in workouts]))
        return exercises
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return []
# Displays user workout hsitory in the table
def show_workout_history(student_id, table):
    # Clears existing entries in the table
    table.delete(*table.get_children())
    workouts = get_workouts(student_id)
    # Inserts each workout into the table
    for workout_id, date, exercise, reps, weight, is_bodyweight in workouts:
        table.insert("", "end", values=(workout_id, date, exercise, reps, weight, "Yes" if  is_bodyweight else "No"))

# Deletes selected workout from the database
def delete_workout(student_id, table):
    try:
        selected = table.selection()
        if not selected:
    # If user does not select a workout to delete a popup will tell them to do so
            messagebox.showerror("Selection Error", "Please select a workout to delete.")
            return
        
        workout_id = table.item(selected[0])["values"][0]

        conn = sqlite3.connect("fitness.db")
        cursor=conn.cursor()
        cursor.execute("DELETE FROM user_workouts WHERE id=? AND student_id=?", (workout_id, student_id,))
        conn.commit() # commits all changes to the database
        conn.close() # closes the connection to the database
        # Notifies the user that the workout has been deleted successfully
        messagebox.showinfo("Deleted", f"workout {workout_id} removed successfully.")
        show_workout_history(student_id, table)
    except Exception as e:
        messagebox.showerror("Error", str(e))
# user logs a workout to the database but there are many validation checks implemented to ensure that data is inputted in a valid form
def log_workout(student_id, workout_entry, exercise_dropdown, exercise_var, workout_table):
    workout = workout_entry.get().strip()
    # Makes sure workout field is not empty and tells the user to enter a workout
    if not workout:
        messagebox.showerror("Input Error", "Please enter a workout.")
        return
    
    
    try:
        parts = [p.strip() for p in workout.split(",")]
        if len(parts) != 4:
            raise ValueError("Format: exercise, reps, weight, is_bodyweight (1 or 0)")
        # Data entry in logging the workouts
        exercise = parts[0].lower() # First enter exercise in lower case
        reps = int(parts[1]) # Second eter the reps as a positive integer
        weight = float(parts[2]) # Third enter the weight as a positive float
        is_bodyweight = int(parts[3]) # Fourth enter 1 for bodyweight exercise and 0 for otherwise
       # Validates. whether the inputs for reps and weights are positive numbers
        if reps <= 0: # Reps must be positive
           messagebox.showerror("Input Error", "Reps and Weight must be positive numbers.")
           return
        if weight < 0: # Weights must be positive
            # Message will be recieved if otherwise
            messagebox.showerror("Input Error", "Reps and Weight must be positive numbers.")
            return
       # must be either 1 or 0 or error will be raised
        if is_bodyweight not in (0, 1): # If statement to validate the data entry
            raise ValueError("is_bodyweight must be 1 (True) or 0 (False)")
        # Defines a lsit of exercises that the system considers valid
        valid_exercises = ["situps" , "pushups", "squat", "deadlift", "bench press", "leg press", "pullups", "row", "lateral raises", "plank", "lunge", "bicep curl", "tricep curl"]
        if exercise not in valid_exercises: # if not in the list error will be raised
            messagebox.showerror("Input Error", f"{exercise} is not a valid exercise.")
            return
        hong_kong = pytz.timezone("Asia/Hong_Kong") # makes sure that current time is set to Hong Kong timezone
        timestamp = datetime.now(hong_kong).strftime("%Y-%m-%d %H:%M:%S") # date format
        # If data is in the valid format the workout will be logged to the database in user_workouts
        add_workout(student_id, exercise, reps, weight, is_bodyweight, timestamp)
        messagebox.showinfo("Success", f"workout logged: {exercise}, ({reps} reps, {weight} kg, bodyweight={is_bodyweight})")
        workout_entry.delete(0, tk.END)

        exercises = get_exercise_list(student_id)
        exercise_dropdown['values'] = exercises
        exercise_var.set(exercise)
        # Refresh the workout history table to show the newly logged workout
        show_workout_history(student_id, workout_table)


    except Exception as e:
        messagebox.showerror("Input Error", str(e))

# checks if use wants to delete their account and deletes all data associated with their account from the database
def delete_account(student_id):
    if messagebox.askyesno("confirm Delete", f"are you sure you want to delete account {student_id}?"):
        try:
            cursor.execute("DELETE FROM users WHERE student_id = ?", (student_id,))
            conn.commit()
            messagebox.showinfo("Account Deleted", f"Account {student_id} has been removed.")
        except Exception as e: # catches any errors
            messagebox.showerror("Error", str(e))    
def add_users(student_id, name, password):
    try:
        conn = sqlite3.connect("fitness.db") # connects to the database
        cursor = conn.cursor()
        # allows user to be added to the users table
        cursor.execute("INSERT INTO users (student_id, name, password) VALUES (?, ?, ?)", (student_id, name, password))
        conn.commit()
        messagebox.showinfo("Success", f"User {name} added with student ID {student_id}.")
    except sqlite3.IntegrityError:
        # if student exists an error message will be shown
        messagebox.showerror("Error", f"student ID {student_id} already exists.")
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", str(e))

    finally:
        conn.close() # finally clsoses the connection to the database


# Charts
import os
import sys
import subprocess
# Opens the saved chart file using the default image viewer based on the operating system
def open_file(filename):
    try:
        if sys.platform.startswith("darwin"):
            subprocess.call(("open", filename))
        elif sys.platform.startswith("win"):
            subprocess.call(["start", "", filename], shell=True)
        elif sys.platform.startswith("linux"):
            subprocess.call(["xdg-open", filename])
    except Exception as e:
        messagebox.showwarning("Open File", f"Chart saved but could not be opened automatically. \n{e}")

  
# Generates and shows a chart that visualizes the user's progress for a specific exercise
def show_progress_chart(student_id, exercise):
    exercise = exercise.strip().lower()
    if not exercise: # makes sure user has selected an exercise
        messagebox.showerror("Input Error", "Please select an exercise.")
        return
    try: # fetches workout data for the selected exercise
        dates, reps, weights = get_workout_data(student_id, exercise)
        if not dates: # if no data is found for the exercise an error will be raised
            messagebox.showerror("Data Error", f"No workout data found for {exercise}.")
            return
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
        # makes sure that reps chart is shon in blue and plotted as dots
        ax1.plot(dates, reps, marker='o', color='blue')
        # Title is set as rpes for the exercise
        ax1.set_title(f"Reps Progress for {exercise.capitalize()}")
        # makes sure y axis is labelled as reps
        ax1.set_ylabel("Reps")
        ax1.grid(True)
       # weights is shown in red and plotted as dots
        ax2.plot(dates, weights, marker='o', color='red')
        ax2.set_title(f"Weights Progress for {exercise.capitalize()}")
        # x axis is set as date and y axis is set as weight in kg
        ax2.set_xlabel("Date")
        ax2.set_ylabel("Weight (Kg)")
        ax2.grid(True)

        plt.xticks(rotation=45)
        plt.tight_layout() # makes sure layout is adjusted properly
        filename = f"progress_{student_id}_{exercise}.png"
        plt.savefig(filename)
        plt.show()
        open_file(filename)
     # Notifies the user that the chart has been generated and saved
        messagebox.showinfo("Chart Generated", f"progress charts saved as {filename}.")
    except Exception as e:
        messagebox.showerror("Error", str(e))
# Dashboard window
def launch_dashboard(student_id, name): # sets up the main dashboard in the app
    root = tk.Tk() # creates the main window using the Tkinter library
    root.title(f"Fitness Dashboard - {name}") # sets up the title of the window
    root.geometry("900x600") # sets up size of the window

    tab_control = ttk.Notebook(root)
    tab_control.pack(expand=1, fill="both") # makes sure tabs expand to fill the window

    exercises = get_exercise_list(student_id)
    exercise_var = tk.StringVar() # variable to hold selected exercise
    exercise_dropdown = ttk.Combobox(tab_control, textvariable=exercise_var, values=exercises, state="readonly")
    

    # Leaderboards Tab
    tab_leaderboard = ttk.Frame(tab_control) # leaderboard tab frame
    tab_control.add(tab_leaderboard, text="Leaderboards") # adds the tab to the dashboard

    tk.Label(tab_leaderboard, text="Leaderboards", font=("Helvetica", 14)).pack(pady=10)
    # sets up the leaderboard table view and it's properties
    leaderboard_table = ttk.Treeview(tab_leaderboard, show="headings")
    leaderboard_table.pack(expand=True, fill="both", pady=10)
    # buttons allowing user to switch between global and perosnal leaderboards
    tk.Button(tab_leaderboard, text="Global Leaderboard", command=lambda: show_global_leaderboard(leaderboard_table)).pack(pady=5)
    tk.Button(tab_leaderboard, text="My Progress", command=lambda: show_personal_leaderboard(leaderboard_table, student_id)).pack(pady=5)
    
    # Predictions Tab
    tab_prediction = ttk.Frame(tab_control)
    tab_control.add(tab_prediction, text="Predictions") # adds predictions tab to the dashboard

    tk.Label(tab_prediction, text="Enter Exercise", font=("Helvetica", 14)).pack(pady=10)
    exercise_entry = tk.Entry(tab_prediction) # entry field for exercise name
    exercise_entry.pack(pady=5)
    # Label for user level display
    level_label = tk.Label(tab_prediction, text="Current Level: Intermediate", font=("Helvetica", 12, "bold"))
    level_label.pack(pady=5) # size and font properties
   # sets up the prediction table where user can see predicted reps and weights
    prediction_table = ttk.Treeview(tab_prediction, columns=("Day", "Reps", "Weight (Kg)", "Reps CI", "Weight CI"), show="headings")
    for col in prediction_table["columns"]:
        prediction_table.heading(col, text=col) # sets up column headings
        prediction_table.column(col, anchor="center", width=120)
    prediction_table.pack(pady=10, expand=True, fill="both") # size propoerties
   # button that allows user to show predictions of a selected exercise enables both prediction plot and prediction table
    tk.Button(tab_prediction, text="Show Predictions", command=lambda: show_predictions(student_id, exercise_entry, level_label, prediction_table)).pack(pady=10)

    # workouts Tab
    tab_workouts = ttk.Frame(tab_control)
    tab_control.add(tab_workouts, text="workouts") # adds the workouts tab to the dashboard

    tk.Label(tab_workouts, text="Add Workout", font=("Helvetica", 12)).pack(pady=10) # Text, size and font properties
  # shows user the correct format to enter their workout and shows them a list of valid exercises
    tk.Label(tab_workouts, text="Enter Workout (exercise, reps, weight, is_bodyweight (1 or 0) - saved with your name, Valid exercises include situps, pushups, squat, deadlift, bench press, leg press, pullups, row, lateral raises, plank, lunge, bicep curl, tricep curl", 
    font=("Helvetica", 10), fg="gray").pack(pady=2)

    workout_entry = tk.Entry(tab_workouts, width=50) # Entry field for logging workouts
    workout_entry.pack(pady=5)

    exercises = get_exercise_list(student_id) # fetches exercise list for dropdown menu
    exercise_var = tk.StringVar() # variable holds slected exercise
    # dropdown menu for deleting account
    exercise_dropdown = ttk.Combobox(tab_workouts, textvariable=exercise_var, values=exercises, state="readonly")
    exercise_dropdown.pack(pady=5)
   # the button that allows a user to delete their account from the database
    delete_button = tk.Button(tab_workouts, text="Delete Account", command=lambda: delete_account(student_id))
    delete_button.pack(pady=5)
# Buttons that allow the user to ladd a workout entry to the database and delete a selected workout entry from the database
    tk.Button(tab_workouts, text="Add Workout", command=lambda: log_workout(student_id, workout_entry, exercise_dropdown, exercise_var, workout_table)).pack(pady=5)
    tk.Button(tab_workouts, text="Delete Selected Workout", command=lambda: delete_workout(student_id, workout_table)).pack(pady=5)
    tk.Label(tab_workouts, text="Workout History", font=("Helvetica", 12)).pack(pady=10) # Tex, size and font properties

    # This table shows the user's workout history directly on the workouts tab

    workout_table = ttk.Treeview(tab_workouts, columns=("ID", "Datetime", "Exercise", "Reps", "Weight", "Bodyweight"), show="headings")
    workout_table.heading("ID", text="ID") # ID column heading
    workout_table.heading("Datetime", text="Datetime") # Datetime column heading
    workout_table.heading("Exercise", text="Exercise") # exercise column heading
    workout_table.heading("Reps", text="Reps") # Reps column heading
    workout_table.heading("Weight", text="Weight (Kg)") # Weight column heading
    workout_table.heading("Bodyweight", text="Bodyweight (1=True, 0=False)") # Bodyweight column heading
   # Size properties for the workout history table
    workout_table.pack(expand=True, fill="both", pady=10)




    show_workout_history(student_id, workout_table) # Poulates the workout history table with user data

# Charts Tab
    tab_charts = ttk.Frame(tab_control)
    tab_control.add(tab_charts, text="Charts") # adds the charts tab to the dashboard
    # size properties of thee charts tab
    tk.Label(tab_charts, text="Visualize Progress", font=("Helvetica", 12)).pack(pady=10)
    # Dropdown menu to select exercise to generate a chart for
    exercise_dropdown = ttk.Combobox(tab_charts, state="readonly")
    # fetches exercise list for the dropdown menu
    exercises = get_exercise_list(student_id)
    # checks if exercises is a string and converts it to a list if so
    if isinstance(exercises, str):
        # Ensures that exercises is a list even if a single exercise is returned as a string
        exercises = [exercises]

    exercise_dropdown['values'] = exercises
    # binds the dropdown menu to the exercise variable
    exercise_dropdown.pack(pady=5)
    # sets the default selected exercise to the first in the list
    if exercises:
       # makes sure that current selection is the first exercise in the list
       exercise_dropdown.current(0)
     # The button that when the user presse generates and shows the progress chart for the selected exercise
    tk.Button(tab_charts, text="Generate Chart", command=lambda: show_progress_chart(student_id, exercise_dropdown.get())).pack(pady=10)

    tab_control.pack(expand=1, fill="both")
    # allows the dashboard window to run
    root.mainloop()


# ensures that student id is unique for registartion
def is_student_id_taken(student_id):
     conn = sqlite3.connect("fitness.db") # connects to the database
     cursor = conn.cursor()
     # Checks if student id is already in the users table
     cursor.execute("SELECT 1 FROM users WHERE student_id = ?", (student_id,))
     exists = cursor.fetchone() is not None
     conn.close()
     return exists


# Welcome and login page
login_window = tk.Tk()
login_window.title("Fitness Tracker Login")
login_window.geometry("400x400")
# welcomes user to the app
tk.Label(login_window, text="Welcome to Fitness Planet!", font=("Helvetica", 16)).pack(pady=20)
tk.Label(login_window, text="Student ID: ").pack(pady=5)
entry_id = tk.Entry(login_window) # entry field for student id
entry_id.pack(pady=5)

tk.Label(login_window, text="Password:").pack(pady=5)
entry_pw = tk.Entry(login_window, show="*")
entry_pw.pack(pady=5)

def login():
    student_id = entry_id.get()
    password = entry_pw.get()

    if not student_id.isdigit() or not (1000 <= int(student_id) <= 999999):
        messagebox.showerror("Login Error", "Student ID must be between 4-6 digits.")
        return
    
    conn = sqlite3.connect("fitness.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, password FROM users WHERE student_id = ? LIMIT 1 ", (int(student_id), ))
    result = cursor.fetchone()
    conn.close()
    

    if result:
        name, stored_pw = result
        if password == stored_pw:
            messagebox.showinfo("Login successful", f"welcome, {name}!")
            login_window.destroy()
            launch_dashboard(int(student_id), name)
        else: 
            messagebox.showerror("Login Error", "incorrect password.") 
    else:
           messagebox.showerror("Login Error", "Student ID not found.")
def open_registration():
    reg_window = tk.Toplevel()
    reg_window.title("user Registration")
    reg_window.geometry("400x350")

    tk.Label(reg_window, text="name:").pack(pady=5) # enter name in register window
    name_entry = tk.Entry(reg_window)
    name_entry.pack(pady=5)

    tk.Label(reg_window, text="Student ID:").pack(pady=5) # enter student id in register window
    id_entry = tk.Entry(reg_window)
    id_entry.pack(pady=5)

    tk.Label(reg_window, text="password:").pack(pady=5) # enter password in register window
    pw_entry = tk.Entry(reg_window, show="*")
    pw_entry.pack(pady=5)
    
    def check_id_availability(event):
        sid = id_entry.get()
        if sid.isdigit() and is_student_id_taken(int(sid)): # checks if student id is available
            messagebox.showwarning("ID Taken", "student Id is already taken.")
            # If not available a warning message will be shown
        else:
            messagebox.showinfo("ID Available", "STudent ID is available.")

    id_entry.bind("<KeyRelease>", check_id_availability)

    

    def register():
        name = name_entry.get()
        student_id = id_entry.get()
        password = pw_entry.get()
# must have name, student_id and password to register
        if not name or not student_id.isdigit() or not (1000 <= int(student_id) <= 999999) or not password:
            messagebox.showerror("Registration Error", "please fill all fields correctly.")
            return
        if len(password) < 6: # ensures password is at least 6 characters long 
            messagebox.showerror("Weak password", "Password must be at least 6 characters long.")
            return
        if is_student_id_taken(int(student_id)): # raises error if student id is already taken
            messagebox.showerror("Error", "Student ID is alrady taken")
            return

        
        conn = sqlite3.connect("fitness.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (student_id, name, password) VALUES (?, ?, ?)", (int(student_id), name, password))

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Account created successfully!")
        reg_window.destroy() # destroys the registration window after successful registration

    tk.Button(reg_window, text="Create account", command=register).pack(pady=10)

tk.Button(login_window, text="Login", command=login).pack(pady=10)
tk.Button(login_window, text="register", command=open_registration).pack(pady=5)
login_window.mainloop() # starts the loop where after user logs in the dashboard will open



   
  


     

    
  

