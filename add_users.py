import sqlite3

conn = sqlite3.connect("fitness.db")
cursor = conn.cursor()

users = [("John", "three123"), ("Jamies", "Steve123"), ("Ashton", "crazy123"), ("Jamie", "king123"),]
cursor.executemany("INSERT INTO users (name, password) VALUES (?, ?)", users)
conn.commit()
conn.close()