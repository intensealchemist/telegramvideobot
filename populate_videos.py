import sqlite3

def add_video(file_id):
    conn = sqlite3.connect('videos.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_id TEXT NOT NULL
    )
    ''')

    cursor.execute("INSERT INTO videos (file_id) VALUES (?)", (file_id,))
    conn.commit()
    conn.close()

    print(f"Video file_id '{file_id}' added successfully!")

if __name__ == "__main__":
    file_id = input("Enter the video file_id: ")
    add_video(file_id)
