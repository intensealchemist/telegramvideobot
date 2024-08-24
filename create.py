import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('videos.db')
cursor = conn.cursor()

# Create the videos table
cursor.execute('''
CREATE TABLE IF NOT EXISTS videos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id TEXT NOT NULL
)
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Table created successfully!")
