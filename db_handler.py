import sqlite3
import os

def db_check() -> None:
    if not os.path.exists("stats.db"):
        conn = sqlite3.connect("stats.db")
        c = conn.cursor()
        c.execute("CREATE TABLE stats ("
                  "user_id INTEGER PRIMARY KEY, "
                  "generate_count INTEGER DEFAULT 0, "
                  "encrypt_count INTEGER DEFAULT 0, "
                  "decrypt_count INTEGER DEFAULT 0)")
        conn.commit()
        conn.close()
        print("База stats.db создана")

def update_stats(user_id, command):
    conn = sqlite3.connect("stats.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO stats (user_id) VALUES (?)", (user_id,))
    if command == "generate":
        c.execute("UPDATE stats SET generate_count = generate_count + 1 WHERE user_id = ?", (user_id,))
    elif command == "encrypt":
        c.execute("UPDATE stats SET encrypt_count = encrypt_count + 1 WHERE user_id = ?", (user_id,))
    elif command == "decrypt":
        c.execute("UPDATE stats SET decrypt_count = decrypt_count + 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()