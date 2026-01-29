import sqlite3

conn = sqlite3.connect("fitness.db")
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(user_workouts)")
print(cursor.fetchall())
# Allows you to see the base structure of the database table user_workouts