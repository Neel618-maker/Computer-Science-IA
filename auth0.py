import sqlite3
import bcrypt 

def register(email, password):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    conn = sqlite3.connect("fitness.db")
    conn.execute("INSERT INTO users (email, password_hash) VALUES (?, ?)", (email, hashed))
    conn.commit()
    conn.close()

def login(email, password):
    conn = sqlite3.connect("fitness.db")
    cursor = conn.execute("SELECT user_id, password_hash FROM users WHERE email=?", (email,))
    result = cursor.fetchone()
    conn.close()
    if result and bcrypt.checkpw(password.encode(), result[1]):
        return result[0]
    return None