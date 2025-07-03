import sqlite3


def init_db():
    sqlite = sqlite3.connect("../dbs/sqlite.db")
    cursor = sqlite.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tickets (
        ID TEXT PRIMARY KEY,
        name TEXT,
        SlaTimeBreak INTEGER            
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users(
        userTG TEXT PRIMARY KEY,
        nameYouTrack TEXT,
        fullName TEXT,
        ringID TEXT,
        tickets TEXT      
    )''')
    sqlite.commit()

if __name__ == "__main__":
    init_db()