import telebot
import config
import utils.ticketsAPI as ticketsAPI
import time
import random
import urllib3
import utils.filesAPI as fileAPI
import utils.db as db

from datetime import datetime as dt
from threading import Thread
from telebot import types
from loguru import logger

callbacks = {
    'docs': ["doc_type: 1", "doc_type: 2", "doc_type: 3"],
    'manage_access': ["add", "remove", "remove_user"],
}

#Сильный костыль конешн, но я не нашел в доке как мне передавать контекст через степ хендлеры, поэтому пока так

cancel = types.InlineKeyboardButton("Отменя", callback_data="cancel")

bot = telebot.TeleBot(config.api)
assignee_from_group = False
type_of_docs = 0
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

@bot.message_handler(commands=["pong"])
def assignee_time_message():
    current_user, next_user = ticketsAPI.read_schedule()
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
    global assignee_from_group
    logger.info(f"Started assignee func by {message.from_user.username}")
    message.text = message.text.replace("start ","")    
    try: 
        print(len(str(message.text).split(" ")))
        current_user, next_user = ticketsAPI.read_schedule()
        print(f"Message get from @{message.from_user.username} and current_user by schedule is {current_user} and next user is {next_user}")
        if message.text == "/assignee":
            if f"@{message.from_user.username}" == config.user_tg[current_user] or f"@{message.from_user.username}" == config.user_tg[next_user]:
                if not(assignee_from_group):
                    name = ticketsAPI.assigne_to_next()
                    bot.send_message(message.chat.id, f"🖊️Переназначение на основе расписания🖊️\nНазначено: {name}")
                    assignee_from_group = True
                    logger.info(f"Assignee from {current_user} to {next_user}")
                else:
                    print(f"Already assigned")
            else:
                print("User are not allowed to assignee")
        elif len(message.text.split(" ")) == 2:
            next_user = message.text.split(" ")[1]
            name = ticketsAPI.assigne_to_next(next_user_param=next_user)
            bot.send_message(message.chat.id, f"📎Переназначение на конкретного пользователя📎\nНазначено:{name}")
        elif len(message.text.split(" ")) == 3:
            old_user = message.text.split(" ")[1]
            next_user = message.text.split(" ")[2]
            name = ticketsAPI.assigne_to_next(old_user_param=old_user, next_user_param=next_user)
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
        if (dt.now().hour == 6 + config.timezone or dt.now().hour == 18 + config.timezone) and message_sended != True:
            assignee_time_message()
            message_sended = True
        time.sleep(30)


@bot.message_handler(commands=["start"])
def start(message):
    if "assignee" in message.text:
        #assigne_to_user(message)
        pass #remove
    elif "spam" in message.text:
        logger.info("Sending spam request")
        ticket_id = message.text.split("_")[1]
        ticketsAPI.spam_ticket(ticket_id)
        bot.send_message(message.chat.id, f"Тикет {ticket_id} помечен как спам")

@bot.message_handler(commands=["roulette"], func = lambda message: check_author_and_format(message))
def roulette(message):
    if "l1" in message.text:
        person = config.users[random.randrange(0,4)]
    else:
        person = config.users[random.randrange(5,len(config.users))]
    bot.send_message(message.chat.id, f"Победитель сегодняшней лотерии🎰\n@{person}!\nПоздравляем и/или сочувствуем🫡")

@bot.message_handler(commands=['tickets_count'], func= lambda message : check_author_and_format(message))
def get_tickets_count(message):
    logger.info(f"Get request for count tickets by {message.from_user.username}")
    current_user, _ = ticketsAPI.read_schedule()
    tickets = ticketsAPI.get_tickets(current_user)
    logger.info(f"Get {len(tickets)} tickets")
    bot.send_message(message.chat.id, f"На данный момент на первой линии всего {len(tickets)} тикетов")

@bot.message_handler(commands=['docs'], func= lambda message: check_author_and_format(message))
def make_docs(message):
    params = message.text.split(" ")
    if len(params) == 1:
        markup = types.InlineKeyboardMarkup()
        markup1 = types.InlineKeyboardButton("Управление объемом и размещением табличных пространств Баз данных", callback_data="doc_type: 3")
        markup2 = types.InlineKeyboardButton("Контроль создания резервных копий (Видеодетектор)", callback_data="doc_type: 2")
        markup3 = types.InlineKeyboardButton("Проверка срабатывания и уведомлений систем мониторинга", callback_data="doc_type: 1")
        markup.add(markup1,markup2,markup3,cancel)
        bot.send_message(message.chat.id, text="Выберите вариант отчета для генерации", reply_markup=markup)

@bot.callback_query_handler(lambda call: call.data == "cancel")
def cancel_callback_handler(call):
    try:
        global user_to_manage
        user_to_manage = ""
        bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
        bot.answer_callback_query(call.id, "Операция отменена")
        bot.edit_message_text("Операция отменена", chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    except:
        pass #небольшой похуй)

@bot.callback_query_handler(lambda call: call.data in callbacks['docs'])
def docs_callback_handler(call):
    try:
        bot.edit_message_text("Введите номер РР", chat_id=call.message.chat.id, message_id=call.message.message_id)
        global type_of_docs 
        type_of_docs = call.data.split(": ")[1]
        bot.register_next_step_handler(call.message, fileAPI.make_docx_file, type_of_docs, bot)
        logger.info("Started making docx file func")
        bot.answer_callback_query(call.id)
    except Exception as e:
        logger.error(f"Making docs stoped with error {e}") 

@bot.callback_query_handler(lambda call: call.data in callbacks['manage_access'])
def manage_access_callback_handler(call):
    try:
        if call.data == "add":
            markup_second = types.InlineKeyboardMarkup()
            markup_second.add(cancel)
            bot.edit_message_text("Введите тикеты, к которым требуется выдать доступ", call.message.chat.id, call.message.message_id)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup_second)
            bot.register_next_step_handler(call.message, manage_access_to_view_ticket_add)
        #elif call.data == "remove":
        #    markup_second = types.InlineKeyboardMarkup()
        #    markup_second.add(cancel)
        #    bot.edit_message_text("Введите тикеты, к которым требуется забрать доступ", call.message.chat.id, call.message.message_id)
        #    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup_second)
        #    bot.register_next_step_handler(call.message, manage_access_to_view_ticket_rem)
    except Exception as e:
        logger.error(f"Something gone wrong with error {e}")
 
@bot.message_handler(commands=["manage_access"], func=lambda message: check_author_and_format(message))
def manage_access_to_view_ticket(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(cancel)
    bot.send_message(message.chat.id, text="Укажите ID пользователя в Телеграм", reply_markup=markup)
    bot.register_next_step_handler(message, manage_access_to_view_ticket_follow_up)

def manage_access_to_view_ticket_follow_up(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(cancel)
    if len(message.text.strip().split(" ")) > 1:
        bot.send_message(message.chat.id, text="Укажите одного пользователя",reply_markup=markup)
        bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
        bot.register_next_step_handler(message, manage_access_to_view_ticket_follow_up)
    else:
        if message.text.startswith("@"): message.text = message.text[1:]
        global user_to_manage
        user_to_manage = message.text.lower()
        markup = types.InlineKeyboardMarkup()
        markup_but1 = types.InlineKeyboardButton("Добавить доступ к тикету", callback_data="add")
        markup_but2 = types.InlineKeyboardButton("Удалить доступ к тикету", callback_data="remove")
        markup.row(markup_but1, markup_but2)
        markup.row(cancel)
        bot.send_message(message.chat.id, text="Выберите опцию", reply_markup=markup)
#TODO: Вынести команды в отдельный файл и там сделать красивый код
def manage_access_to_view_ticket_add(message):
    global user_to_manage
    tickets = message.text.strip().split(" ")
    error = []
    goods = []
    for ticket in tickets:
        ticket.strip()
        if not ticket.upper().startswith("SUP-"): error.append(ticket)
        elif len(ticket) != 9: error.append(ticket)
        else: goods.append(ticket.upper())
    error = [err for err in error if err.strip()]
    goods = [good for good in goods if good.strip()]
    result = ""
    try: db.set_tickets_to_user(user_to_manage, " ".join(goods))
    except Exception as e:
        user_to_manage 
        logger.error(e)
    user_to_manage = ""
    if len(error) > 0:
        result += "*Ошибка при обработке тикетов*: \n" + ", ".join(error) + "\n\n"
    if len(goods) > 0: result += "*Успешно добавленные тикеты*: \n" + ", ".join(goods)
    bot.send_message(message.chat.id, parse_mode="Markdown", text=result)

#TODO: Тот же самый коммент что и выше, вынести команды и сделать красивее
#TODO: Доделать функцию для удаления тикетов в базе, начать делать запрос тикета по номеру, расскоментить хендлер на rem
#def manage_access_to_view_ticket_rem(message):
#    print(manage_context)
#    tickets = message.text.strip().split(" ")
#    error = []
#    goods = []
#    for ticket in tickets:
#        ticket.strip()
#        if not ticket.upper().startswith("SUP-"): error.append(ticket)
#        elif len(ticket) != 9: error.append(ticket)
#        else: goods.append(ticket.upper())
#    error = [err for err in error if err.strip()]
#    goods = [good for good in goods if good.strip()]
#    result = ""
#    #try: db.set_tickets_to_user(user, " ".join(goods))
#    #except Exception as e: 
#    #    logger.error(e)
#    if len(error) > 0:
#        result += "*Ошибка при обработке тикетов*: \n" + ", ".join(error) + "\n\n"
#    if len(goods) > 0: result += "*Успешно удаленные тикеты*: \n" + ", ".join(goods)
#    bot.send_message(message.chat.id, parse_mode="Markdown", text=result)

if __name__ == "__main__":
    logger.info(f"Bot started {bot.get_my_name()}")
    schedule_thread = Thread(target=schedule_message)
    schedule_thread.start()
    bot.polling()
