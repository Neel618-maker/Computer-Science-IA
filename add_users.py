import sqlite3

conn = sqlite3.connect("fitness.db")
cursor = conn.cursor()

users = [("Neel", "mypassword123"), ("Alex", "securepass456"), ("Maya", "workout789"), ("Ravi", "fitnesslover"),]
cursor.executemany("INSERT INTO users (name, password) VALUES (?, ?)", users)
conn.commit()
conn.close()