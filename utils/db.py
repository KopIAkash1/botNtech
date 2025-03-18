import sqlite3

db = sqlite3.connect("allowed_to_tickets.db", check_same_thread=False)
cursor = db.cursor()

#Функцию вызывать с параметрами add_tickets_to_user(user, tickets="")
def set_tickets_to_user(user, tickets):
    if not __is_user_exist(user): __set_user(user, tickets)
    __set_tickets(user, tickets)
    
#Возвращает все тикеты пользователя как строка, обрабатываем там, откуда вызывали
#Если вызываем и выдает None -> return "Пользователь не найден" или чонить подобное
def get_tickets_by_user(user) -> str:
    if not __is_user_exist(user): return None
    else: return __get_tickets(user)
        


#__*****() ИЗВНЕ НЕ ВЫЗЫВАТЬ!!!
def __is_user_exist(user) -> bool:
    cursor.execute("SELECT TelegramUser FROM users WHERE TelegramUser = ?", (user,))
    return cursor.fetchone() is not None

def __set_user(user, tickets):
    cursor.execute("INSERT INTO users (TelegramUser) VALUES (?)", (user,))
    db.commit()
    set_tickets_to_user(user, tickets)

def __set_tickets(user, tickets):
    cursor.execute("UPDATE users SET tickets = ? WHERE TelegramUser = ?", (tickets.strip(), user,))
    db.commit()

def __get_tickets(user) -> str :
    cursor.execute("SELECT tickets FROM users WHERE TelegramUser = ?", (user,))
    result = cursor.fetchone()[0]
    return result