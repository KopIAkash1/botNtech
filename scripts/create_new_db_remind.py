import sqlite3

con = sqlite3.connect("../remind_tickets.db")

cursor = con.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS tickets (
    TicketId TEXT PRIMARY KEY,
    timestampRemindTime INTEGER
)
''')

con.commit()