import os
import sqlite3

db_path = r'C:\Users\Devan\OneDrive\Desktop\SEM 4\Portfoilio Tracking\Portfolio-tracker\Portfolio-tracker\portfolio.db'

# Check if the file exists
if os.path.exists(db_path):
    print("Database found. Connecting to the existing database.")
    conn = sqlite3.connect(db_path)
else:
    print("Database file not found! Creating a new one.")
    conn = sqlite3.connect(db_path)

cursor = conn.cursor()

# Example query to check the tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in the database:", tables)

conn.close()
