import telebot
import config
import time
import urllib3
import utils.ticketsAPI as ticketsAPI 

from datetime import datetime as dt
from threading import Thread
from telebot import types
from loguru import logger
from commands import callback_handlers, test_commands, tickets_commands, files_commands

bot = telebot.TeleBot(config.api)
type_of_docs = 0
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # and is_tagging(message)

#Тестовые команды
test_commands.init_test_commands(bot)
#Команды с тикетами (Управление доступом, получение тикетов)
tickets_commands.init_manage_access_command(bot)
tickets_commands.init_tickets_managment_commands(bot)
#Команды связанные с файлами (Скриншоты, документы, графики)
files_commands.init_docs_maker(bot)

#Инциализация колбек хендлеров (глобальных, которые юзаются почти везде)
callback_handlers.init_all_callback_handlers(bot)

def is_tagging(message):
    return f'@{bot.get_me().username}' in message.text

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

def schedule_message():
        message_sended = False
        while True:
            if (dt.now().hour == 6 + config.timezone or dt.now().hour == 18 + config.timezone) and message_sended != True:
                assignee_time_message()
                message_sended = True
            time.sleep(30)

if __name__ == "__main__":
    logger.info(f"Bot started {bot.get_my_name()}")
    schedule_thread = Thread(target=schedule_message)
    schedule_thread.start()
    bot.infinity_polling(none_stop=True)