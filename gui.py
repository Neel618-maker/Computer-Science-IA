
# Create GUI window Main page for application
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from workouts import add_workout, get_workouts
from predictor import (get_workout_data, predict_targets, plot_predictions, show_leaderboard)

def is_student_id_taken(student_id):
     conn = sqlite3.connect("fitness.db")
     cursor = conn.cursor()
     cursor.execute("""
        SELECT 1 FROM users WHERE student_id = ?""", (student_id))
     exists = cursor.fetchone() is not None
     conn.close()
     return exists
# Welcome and login page
login_window = tk.Tk()
login_window.title("Fitness Tracker Login")
login_window.geometry("400x400")

tk.Label(login_window, text="welcome to fitness Planet!", font=("Helvetica", 16)).pack(pady=20)
tk.label(login_window, text="Student ID: ").pack(pady=5)
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
    cursor.execute("""
         SELECT name, password FROM users
         WHERE student_id = ? LIMIT1
    """, (int(student_id), ))
    result = cursor.fetchone()
    conn.close()

    if result:
        name, stored_pw = result
        if password == stored_pw:
            messagebox.showinfo("Login successful", f"welcome, {name} !")
            login.window.destroy()
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

     def check_id_availability(event):
          sid = id_entry.get()
          if sid.isdigit () and is_student_id_taken(int(sid)):
               messagebox.showwarning("ID Taken", "student Id is already taken.", fg="red")
          else:
               messagebox.showinfo("ID Available", "STudent ID is available.")

          id_entry.bind("KeyRelease", check_id_availability)
        

     tk.Label(reg_window, text="password:").pack(pady=5)
     pw_entry = tk.Entry(reg_window, show="*")
     pw_entry.pack(pady=5)


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
          cursor.execute("""INSERT INTO users (student_id, name, password) VALUES (?, ?, ?)""", (int(student_id), name, password))

          conn.commit()
          conn.close()

          messagebox.showinfo("Success", "Account created successfully!")
          reg_window.destroy()

          tk.Button(reg_window, text="create account", command=register).pack(pady=10)

          tk.Button(login_window, text="Login", command=login).pack(pady=10)
          tk.Button(login_window, text="register", command=open_registration).pack(pady=5)
          login_window.mainloop()

# Dashboard window
def launch_dashboard(student_id, name):
     root = tk.TK()


     

    
  

