import sqlite3

conn = sqlite3.connect("fitness.db")
cursor = conn.cursor()

print("Tables:")
for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table';"):
    print(row)

print("\nUsers:")
for row in cursor.execute("SELECT * FROM users;"):
    print(row)

print("\nWorkouts:")
for row in cursor.execute("SELECT * FROM user_workouts;"):
    print(row)

conn.close()



    
