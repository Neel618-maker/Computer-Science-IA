import sqlite3
import hashlib
# Validate Password
def is_valid_password(passowrd):
    return len(passowrd) >= 8
# hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Validate student ID format
def is_valid_student_id(sid):
    return sid.isdigit() and 1000 <= int(sid) <= 999999

# register a new user
def add_user(name, house, student_id, password, exercise="none"):
    if not is_valid_student_id(student_id):
        print("Error: Student ID must be a number between a 4-6 digit number.")
        return
    
    student_id = int(student_id)
    hashed_pw = hash_password(password)

    conn = sqlite3.connect("fitness.db")
    cursor = conn.cursor()

    # check for duplicate 
    cursor.execute("SELECT 1 FROM user_workouts WHERE student_id = ?", (student_id,))
    if cursor.fetchone():
        print("Error: Student ID already exists.")
        conn.close()
        return
    
    # insert placeholder row to store identity
    cursor.execute("""
        INSERT INTO user_workouts (name, house, student_id, password, exercise, reps, weight, is_bodyweight)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, house, student_id, hashed_pw, exercise, 0, 0.0, 1))

    conn.commit()
    conn.close()
    print("user registered successfully.")

    # Authenticate User login
    def authenticate_user(student_id, password):
        if not is_valid_student_id(student_id):
            print ("Error: student ID must be 4-6 digit number.")
            return None

        student_id = int(student_id)
        hashed_pw = hash_password(password)

        conn = sqlite3.connect("fitness.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name FROM user_workouts
            WHERE student_id = ? AND password = ?
            LIMIT 1
        """, (student_id, hashed_pw))
        result = cursor.fetchone()
        conn.close()

        if result:
            name = result[0]
            print(f"Login successful. Welcome, {name}!")
            return student_id
        else:
            print("Error: Invalid student ID or password.")
            return None
  
  # Retrieve user info                                                                                     )                                    
def get_user_info(student_id):
    if not is_valid_student_id(str(student_id)):
        return None
    
    student_id = int(student_id)
    conn = sqlite3.connect("fitness.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, house, password FROM user_workouts
        WHERE student_id = ?
        LIMIT 1
    """, (student_id))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            "name": result[0],
            "house": result[1],
            "password": result[2]

        }
    else:
        return None
    
# Delete user and all related data
def delete_user(student_id):
    if not is_valid_student_id(str(student_id)):
        print("Error: student ID must be a 4-6 digit number.")
        return
    
    student_id = int(student_id)
    conn = sqlite3.connect("fitness.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM user_workouts WHERE student_id = ?", (student_id,))
    count = cursor.fetchone()[0]

    if count == 0:
        print("Errror: no user found with that student ID.")
        conn.close()
        return
    
    cursor.execute("DELETE FROM user_workouts WHERE student_id = ?", (student_id,))
    cursor.execute("DELETE FROM user_goals WHERE student_id = ?", (student_id,))

    conn.commit()
    conn.close()
    print(f" User '{student_id}' and all related data deleted.")

    # Update a user
def update_user(student_id, new_name=None, new_house=None, new_password=None):
    conn = sqlite3.connect("fitness.db")
    cursor = conn.cursor()

    fields = []
    values = []

    if new_name is not None:
        fields.append("name = ?")
        values.append(new_name)
    if new_house is not None:
        fields.append("house = ?")
        values.append(new_house)
    if new_password is not None:
        fields.append("password = ?")
        values.append(hash_password(new_password))

    if not fields:
        print("error: No fields tto update")
        conn.close()
        return
    values.append(student_id)
    query =  f"UPDATE user_workouts SET {', '.join(fields)} WHERE student_id = ?"

    cursor.execute(query, values)
    conn.commit()
    conn.close()
    print(f"user {student_id} profile updated.")

    # Updated latest workout for a specific exercise
    def update_exercise(student_id, exercise, new_reps=None, new_weight=None):
        conn = sqlite3.connect("fitness.db")
        cursor = conn.cursor()

        fields = []
        values = []

        if new_reps is not None:
            fields.append("reps =?")
            values.append(new_reps)
        if new_weight is not None:
            fields.append("weight = ?")
            values.append(new_weight)
        if not fields:
            print("Error : no exercise fields to update")
            conn.close()
            return
        
        values.append(student_id)
        values.append(exercise)
        query = f"UPDATE user_workouts SET {', '.join(fields)} WHERE student_id = ? AND exercise = ?"
        
        cursor.execute(query, values)
        conn.commit()
        conn.close()
        print(f"Updated latest {exercise} Workout for use {student_id}.")

