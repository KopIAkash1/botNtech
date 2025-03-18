import sqlite3

con = sqlite3.connect("../allowed_to_tickets.db")

cursor = con.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    TelegramUser TEXT PRIMARY KEY,
    tickets TEXT
)
''')

con.commit()