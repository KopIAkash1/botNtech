import sqlite3
from loguru import logger

db = sqlite3.connect("allowed_to_tickets.db", check_same_thread=False)
cursor = db.cursor()

#Функцию вызывать с параметрами add_tickets_to_user(user, tickets="")
def set_tickets_to_user(user, tickets):
    if not is_user_exist(user): __set_user(user, tickets)
    __set_tickets(user, tickets)

#TODO: реализовать удаление тикетов у пользователя
def rem_tickets_from_user(user, tickets):
    if not is_user_exist(user): return None
    else: _rem_tickets(user, tickets)
    
#Возвращает все тикеты пользователя как строка, обрабатываем там, откуда вызывали
#Если вызываем и выдает None -> return "Пользователь не найден" или чонить подобное
def get_tickets_by_user(user) -> str:
    if not is_user_exist(user): return None
    else: return __get_tickets(user)

def is_user_exist(user) -> bool:
    cursor.execute("SELECT TelegramUser FROM users WHERE TelegramUser = ?", (user.lower(),))
    return cursor.fetchone() is not None


#__*****() ИЗВНЕ НЕ ВЫЗЫВАТЬ!!!

def __set_user(user, tickets):
    cursor.execute("INSERT INTO users (TelegramUser) VALUES (?)", (user.lower(),))
    db.commit()
    set_tickets_to_user(user, tickets)

def __set_tickets(user, tickets):
    new_tickets = tickets
    old_tickets = __get_tickets(user)
    if old_tickets is not None: new_tickets = old_tickets + " " + tickets
    new_tickets = new_tickets.split(" ")
    new_tickets = " ".join(list(dict.fromkeys(new_tickets)))
    cursor.execute("UPDATE users SET tickets = ? WHERE TelegramUser = ?", (new_tickets.strip(), user.lower(),))
    db.commit()

def __get_tickets(user):
    cursor.execute("SELECT tickets FROM users WHERE TelegramUser = ?", (user.lower(),))
    result = cursor.fetchone()[0]
    return result

def _rem_tickets(user, tickets):
    tickets = tickets.split(" ")
    tickets = list(dict.fromkeys(tickets))
    old_tickets = __get_tickets(user).split(" ")
    if old_tickets is None: return 
    for item in tickets:
        try:
            old_tickets.remove(item)
        except Exception as e:
            logger.error(e)
    old_tickets = " ".join(list(dict.fromkeys(old_tickets)))
    cursor.execute("UPDATE users SET tickets = ? WHERE TelegramUser = ?", (old_tickets.strip(), user.lower(),))
    db.commit()