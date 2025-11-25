
# Create GUI window Main page for application
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime
import pytz
from workouts import add_workout, get_workouts
from predictor import (get_workout_data, predict_targets, plot_predictions, show_leaderboard)

#Leaderboard window
def update_leaderboard(table, data, mode="global"):
    table.delete(*table.get_children())
    if mode == "personal":
        table["columns"] = ("col1", "col2", "col3")
        table.heading("col1", text="Rank")
        table.heading("col2", text="Exercise")
        table.heading("col3", text="Rate (Reps/Day)")
        for rank, (exercise, rate) in enumerate(data, start=1):
            table.insert("", "end", values=(rank, exercise, f"{rate:.2f}"))
    else:
        if mode == "global":
         table["columns"] = ("col1", "col2", "col3", "col4", "col5")
         table.heading("col1", text="Rank")
         table.heading("col2", text="student_id")
         table.heading("col3", text="Name")
         table.heading("col4", text="Exercise")
         table.heading("col5", text="Rate (Reps/Day)")
        for rank, row in enumerate(data, start=1):
            student_id, name, exercise, rate = row
            try:
                rate_val = float(rate)
                rate_fmt = f"{rate_val:.2f}"
            except (ValueError, TypeError):
                rate_fmt = str(rate)
            table.insert("", "end", values=(rank, student_id, name, exercise, rate_fmt))
            
def show_global_leaderboard(table):
    try:
        data = show_leaderboard()
        update_leaderboard(table, data, mode="global")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def show_personal_leaderboard(table, student_id):
    try:
        raw_data = show_leaderboard(student_id=student_id)
        personal_data = [(exercise, rate) for _, _, exercise, rate in raw_data]
        update_leaderboard(table, personal_data, mode="personal")
    except Exception as e:
        messagebox.showerror("Error", str(e))
# Predictions
def show_predictions(student_id, exercise_entry):
    exercise = exercise_entry.get().strip().lower()
    if not exercise:
        messagebox.showerror("Input Error", "Please enter an exercise name.")
        return
    try:
        dates, reps, weights = get_workout_data(student_id, exercise)

        if not dates:
            messagebox.showerror("Data Error", f"No workout data found for exercise: {exercise}, inaccurate date.")
            return
        result = predict_targets(dates, reps, weights)
        if result:
            days, future_days, future_reps, future_weights, reps_ci, weights_ci = result
            plot_predictions(days, reps, weights, future_days, future_reps, future_weights, reps_ci, weights_ci, exercise, student_id)
            messagebox.showinfo("Prediction Complete", f"Prediction plot generated for {exercise}.")
        else:
            messagebox.showinfo("Insufficient Data to make a strong prediction")
    except Exception as e:
        messagebox.showerror("Error", str(e))
# Workouts
def add_workout(student_id, exercise, reps, weight, is_bodyweight, timestamp):
    try:
        with sqlite3.connect("fitness.db") as conn:
          cursor = conn.cursor()
          cursor.execute("INSERT INTO user_workouts (student_id, datetime, exercise, reps, weight, is_bodyweight) VALUES (?, ?, ?, ?, ?, ?)", (student_id, timestamp, exercise, reps, weight, is_bodyweight,))
          conn.commit()
          
    except Exception as e:
        messagebox.showerror("Database Error", str(e))

def get_workouts(student_id):
    try:
        conn = sqlite3.connect("fitness.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, datetime, exercise, reps, weight, is_bodyweight FROM user_workouts WHERE student_id=? ORDER BY datetime", (student_id,))
        return cursor.fetchall()
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
        return []
    

def get_exercise_list(student_id):
    try:
        workouts = get_workouts(student_id)
        exercises = sorted(set([w[2] for w in workouts]))
        return exercises
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return []

def show_workout_history(student_id, table):
    table.delete(*table.get_children())
    workouts = get_workouts(student_id)
    for workout_id, date, exercise, reps, weight, is_bodyweight in workouts:
        table.insert("", "end", values=(workout_id, date, exercise, reps, weight, "Yes" if  is_bodyweight else "No"))


def delete_workout(student_id, table):
    try:
        selected = table.selection()
        if not selected:
            messagebox.showerror("Selection Error", "Please select a workout to delete.")
            return
        
        workout_id = table.item(selected[0])["values"][0]

        conn = sqlite3.connect("fitness.db")
        cursor=conn.cursor()
        cursor.execute("DELETE FROM user_workouts WHERE id=? AND student_id=?", (workout_id, student_id,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Deleted", f"workout {workout_id} removed successfully.")
        show_workout_history(student_id, table)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def log_workout(student_id, workout_entry, exercise_dropdown, exercise_var, workout_table):
    workout = workout_entry.get().strip()
    if not workout:
        messagebox.showerror("Input Error", "Please enter a workout.")
        return
    
    
    try:
        parts = [p.strip() for p in workout.split(",")]
        if len(parts) != 4:
            raise ValueError("Format: exercise, reps, weight, is_bodyweight (1 or 0)")
        
        exercise = parts[0].lower() 
        reps = int(parts[1])
        weight = float(parts[2])
        is_bodyweight = int(parts[3])

        if is_bodyweight not in (0, 1):
            raise ValueError("is_bodyweight must be 1 (True) or 0 (False)")
        valid_exercises = ["situps" , "pushups", "squat", "deadlift", "bench press", "leg press", "pullups", "row", "lateral raises", "plank", "lunge", "bicep curl", "tricep curl"]
        if exercise not in valid_exercises:
            messagebox.showerror("Input Error", f"{exercise} is not a valid exercise.")
            return
        hong_kong = pytz.timezone("Asia/Hong_Kong")
        timestamp = datetime.now(hong_kong).strftime("%Y-%m-%d %H:%M:%S")
        
        add_workout(student_id, exercise, reps, weight, is_bodyweight, timestamp)
        messagebox.showinfo("Success", f"workout logged: {exercise}, ({reps} reps, {weight} kg, bodyweight={is_bodyweight})")
        workout_entry.delete(0, tk.END)

        exercises = get_exercise_list(student_id)
        exercise_dropdown['values'] = exercises
        exercise_var.set(exercise)
        show_workout_history(student_id, workout_table)

    except Exception as e:
        messagebox.showerror("Input Error", str(e))


    

# Charts
import os
import sys
import subprocess
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

  

def show_progress_chart(student_id, exercise):
    exercise = exercise.strip().lower()
    if not exercise:
        messagebox.showerror("Input Error", "Please select an exercise.")
        return
    try:
        dates, reps, weights = get_workout_data(student_id, exercise)
        if not dates:
            messagebox.showerror("Data Error", f"No workout data found for {exercise}.")
            return
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
        ax1.plot(dates, reps, marker='o', color='blue')
        ax1.set_title(f"Reps Progress for {exercise.capitalize()}")
        ax1.set_ylabel("Reps")
        ax1.grid(True)

        ax2.plot(dates, weights, marker='o', color='red')
        ax2.set_title(f"Weights Progress for {exercise.capitalize()}")
        ax2.set_xlabel("Date")
        ax2.set_ylabel("Weight (Kg)")
        ax2.grid(True)

        plt.xticks(rotation=45)
        plt.tight_layout()
        filename = f"progress_{student_id}_{exercise}.png"
        plt.savefig(filename)
        plt.show()
        open_file(filename)

        messagebox.showinfo("Chart Generated", f"progress charts saved as {filename}.")
    except Exception as e:
        messagebox.showerror("Error", str(e))
# Dashboard window
def launch_dashboard(student_id, name):
    root = tk.Tk()
    root.title(f"Fitness Dashboard - {name}")
    root.geometry("900x600")

    tab_control = ttk.Notebook(root)
    tab_control.pack(expand=1, fill="both")

    exercises = get_exercise_list(student_id)
    exercise_var = tk.StringVar()
    exercise_dropdown = ttk.Combobox(tab_control, textvariable=exercise_var, values=exercises, state="readonly")

    # Leaderboards Tab
    tab_leaderboard = ttk.Frame(tab_control)
    tab_control.add(tab_leaderboard, text="Leaderboards")

    tk.Label(tab_leaderboard, text="Leaderboards", font=("Helvetica", 14)).pack(pady=10)
    leaderboard_table = ttk.Treeview(tab_leaderboard, show="headings")
    leaderboard_table.pack(expand=True, fill="both", pady=10)

    tk.Button(tab_leaderboard, text="Global Leaderboard", command=lambda: show_global_leaderboard(leaderboard_table)).pack(pady=5)
    tk.Button(tab_leaderboard, text="My Progress", command=lambda: show_personal_leaderboard(leaderboard_table, student_id)).pack(pady=5)
    
    # Predictions Tab
    tab_prediction = ttk.Frame(tab_control)
    tab_control.add(tab_prediction, text="Predictions")

    tk.Label(tab_prediction, text="Enter Exercise", font=("Helvetica", 14)).pack(pady=10)
    excercise_entry = tk.Entry(tab_prediction)
    excercise_entry.pack(pady=5)
    tk.Button(tab_prediction, text="show Predictions", command=lambda: show_predictions(student_id, excercise_entry)).pack(pady=10)

    # workouts Tab
    tab_workouts = ttk.Frame(tab_control)
    tab_control.add(tab_workouts, text="workouts")

    tk.Label(tab_workouts, text="Add Workout", font=("Helvetica", 12)).pack(pady=10)
    tk.Label(tab_workouts, text="Enter Workout (exercise, reps, weight, is_bodyweight (1 or 0) - saved with your name, Valid exercises include situps, pushups, squat, deadlift, bench press, leg press, pullups, row, lateral raises, plank, lunge, bicep curl, tricep curl", 
    font=("Helvetica", 10), fg="gray").pack(pady=2)

    workout_entry = tk.Entry(tab_workouts, width=50)
    workout_entry.pack(pady=5)

    exercises = get_exercise_list(student_id)
    exercise_var = tk.StringVar()
    exercise_dropdown = ttk.Combobox(tab_workouts, textvariable=exercise_var, values=exercises, state="readonly")
    exercise_dropdown.pack(pady=5)

    tk.Button(tab_workouts, text="Add Workout", command=lambda: log_workout(student_id, workout_entry, exercise_dropdown, exercise_var, workout_table)).pack(pady=5)
    tk.Button(tab_workouts, text="Delete Selected Workout", command=lambda: delete_workout(student_id, workout_table)).pack(pady=5)
    tk.Label(tab_workouts, text="Workout History", font=("Helvetica", 12)).pack(pady=10)

    workout_table = ttk.Treeview(tab_workouts, columns=("ID", "Datetime", "Exercise", "Reps", "Weight", "Bodyweight"), show="headings")
    workout_table.heading("ID", text="ID")
    workout_table.heading("Datetime", text="Datetime")
    workout_table.heading("Exercise", text="Exercise")
    workout_table.heading("Reps", text="Reps")
    workout_table.heading("Weight", text="Weight (Kg)")
    workout_table.heading("Bodyweight", text="Bodyweight (1=True, 0=False)")
    workout_table.pack(expand=True, fill="both", pady=10)



    show_workout_history(student_id, workout_table)

# Charts Tab
    tab_charts = ttk.Frame(tab_control)
    tab_control.add(tab_charts, text="Charts")
    tk.Label(tab_charts, text="Visualize Progress", font=("Helvetica", 12)).pack(pady=10)

    exercise_dropdown = ttk.Combobox(tab_charts, state="readonly")
    
    exercises = get_exercise_list(student_id)
    if isinstance(exercises, str):
        exercises = [exercises]

    exercise_dropdown['values'] = exercises
    exercise_dropdown.pack(pady=5)
    if exercises:
       exercise_dropdown.current(0)

    tk.Button(tab_charts, text="Generate Chart", command=lambda: show_progress_chart(student_id, exercise_dropdown.get())).pack(pady=10)

    tab_control.pack(expand=1, fill="both")
    root.mainloop()



def is_student_id_taken(student_id):
     conn = sqlite3.connect("fitness.db")
     cursor = conn.cursor()
     cursor.execute("SELECT 1 FROM users WHERE student_id = ?", (student_id,))
     exists = cursor.fetchone() is not None
     conn.close()
     return exists


# Welcome and login page
login_window = tk.Tk()
login_window.title("Fitness Tracker Login")
login_window.geometry("400x400")

tk.Label(login_window, text="Welcome to Fitness Planet!", font=("Helvetica", 16)).pack(pady=20)
tk.Label(login_window, text="Student ID: ").pack(pady=5)
entry_id = tk.Entry(login_window)
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
            messagebox.showinfo("Login successful", f"welcome, {name} !")
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

    tk.Label(reg_window, text="name:").pack(pady=5)
    name_entry = tk.Entry(reg_window)
    name_entry.pack(pady=5)

    tk.Label(reg_window, text="Student ID:").pack(pady=5)
    id_entry = tk.Entry(reg_window)
    id_entry.pack(pady=5)

    tk.Label(reg_window, text="password:").pack(pady=5)
    pw_entry = tk.Entry(reg_window, show="*")
    pw_entry.pack(pady=5)
    
    def check_id_availability(event):
        sid = id_entry.get()
        if sid.isdigit() and is_student_id_taken(int(sid)):
            messagebox.showwarning("ID Taken", "student Id is already taken.")
        else:
            messagebox.showinfo("ID Available", "STudent ID is available.")

    id_entry.bind("<KeyRelease>", check_id_availability)

    

    def register():
        name = name_entry.get()
        student_id = id_entry.get()
        password = pw_entry.get()

        if not name or not student_id.isdigit() or not (1000 <= int(student_id) <= 999999) or not password:
            messagebox.showerror("Registration Error", "please fill all fields correctly.")
            return
        if len(password) < 6:
            messagebox.showerror("Weak password", "Password must be at least 6 characters long.")
            return
        if is_student_id_taken(int(student_id)):
            messagebox.showerror("Error", "Student ID is alrady taken")
            return
        
        conn = sqlite3.connect("fitness.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (student_id, name, password) VALUES (?, ?, ?)", (int(student_id), name, password))

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Account created successfully!")
        reg_window.destroy()

    tk.Button(reg_window, text="create account", command=register).pack(pady=10)

tk.Button(login_window, text="Login", command=login).pack(pady=10)
tk.Button(login_window, text="register", command=open_registration).pack(pady=5)
login_window.mainloop()


   
  


     

    
  

