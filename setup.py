import sqlite3

conn = sqlite3.connect("task_2.db")
cursor = conn.cursor()
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS sessions (
        user_id TEXT PRIMARY KEY,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
"""
)
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
"""
)

users = {}
while True:
    option = input("Create new user (c), or q to quit: ")
    match option.lower():
        case "c":
            username = input("Username: ")
            password = input("Password: ")
            users[username] = password
        case "q":
            break
        case _:
            print("Invalid option, try again")

index = 0
for username in users.keys():
    cursor.execute(
        """
        INSERT INTO users (id, username, password)
        VALUES (?, ?, ?)
        """,
        (index, username, users[username]),
    )
    index += 1

conn.commit()
conn.close()
