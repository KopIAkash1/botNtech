import telebot
import config
import assigneeAPI
from threading import Thread
from telebot import types
import datetime
import time

bot = telebot.TeleBot(config.api)
assignee_from_group = False

@bot.message_handler(commands=["pong"])
def assignee_time_message():
    current_user, next_user = assigneeAPI.read_schedule()
    msg = f'''🎉Переназначение🎉\
    \nТекущий пользователь: {current_user}\
    \nСледующий пользователь: {next_user}
    '''
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("Переназначить", url="https://t.me/TicketTrackerNTECHbot?start=assignee")
    markup.add(button1)
    bot.send_message(chat_id=config.group_chat_pid, text=msg, reply_markup=markup, reply_to_message_id=172548)

@bot.message_handler(commands=["assignee"], func=lambda message: check_author_and_format(message))
def assigne_to_user(message):
    message.text = message.text.replace("start ","")    
    try: 
        print(len(str(message.text).split(" ")))
        current_user, next_user = assigneeAPI.read_schedule()
        print(f"Message get from @{message.from_user.username} and current_user by schedule is {current_user}")
        if message.text == "/assignee" and f"@{message.from_user.username}" == config.user_tg[current_user]:
            name = assigneeAPI.assigne_to_next()
            if not(assignee_from_group):
                bot.send_message(message.chat.id, f"🖊️Переназначение на основе расписания🖊️\nНазначено: {name}")
                assignee_from_group = True
        elif len(message.text.split(" ")) == 2:
            next_user = message.text.split(" ")[1]
            name = assigneeAPI.assigne_to_next(next_user_param=next_user)
            bot.send_message(message.chat.id, f"📎Переназначение на конкретного пользователя📎\nНазначено:{name}")
        elif len(message.text.split(" ")) == 3:
            old_user = message.text.split(" ")[1]
            next_user = message.text.split(" ")[2]
            name = assigneeAPI.assigne_to_next(old_user_param=old_user, next_user_param=next_user)
            bot.send_message(message.chat.id, f"🤝Переназначение с одного на другого пользователя🤝\nТикеты с {old_user}\nНазначены на {next_user}")
    except Exception as e: print(F"WARNING | Get exception in message. Message: {message.text}\n{e}")

def is_tagging(message):
    return f'@{bot.get_me().username}' in message.text

def check_author_and_format(message):
    return message.from_user.username in config.users # and is_tagging(message)

@bot.message_handler(commands=['get_channel_id_for_chat'], func=lambda message: check_author_and_format(message))
def get_channel_id(message):
    bot.send_message(message.chat.id, f"ID чата: {message.chat.id}\nThread чата: {message.message_thread_id}",reply_to_message_id=message.message_id)

def schedule_message():
    message_sended = False
    while True:
        if (datetime.datetime.now().hour == 9 or datetime.datetime.now().hour == 21) and message_sended != True:
            assignee_time_message()
            message_sended = True
        time.sleep(30)


@bot.message_handler(commands=["start"])
def start(message):
    if "assignee" in message.text:
        assigne_to_user(message)



if __name__ == "__main__":
    schedule_thread = Thread(target=schedule_message)
    schedule_thread.start()
    bot.polling()