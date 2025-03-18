import sqlite3

db = sqlite3.connect("allowed_to_tickets.db", check_same_thread=False)
cursor = db.cursor()

def add_tickets_to_user(user, tickets):
    if not __is_user_exist(user): __add_user(user, tickets)
    
#TODO: Доделать вытаскивание тикетов для дальнейшей проверки
def get_tickets_by_user(user) -> str:
    pass
        


#__*****() ИЗВНЕ НЕ ВЫЗЫВАТЬ!!!
def __is_user_exist(user):
    cursor.execute("SELECT TelegramUser FROM users WHERE TelegramUser = ?", (user,))
    return cursor.fetchone() is not None

def __add_user(user, tickets):
    cursor.execute("INSERT INTO users (TelegramUser) VALUES (?)", (user,))
    db.commit()
    add_tickets_to_user(user, tickets)