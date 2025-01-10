import telebot
import subprocess
from telebot import types
import os
import config

bot = telebot.TeleBot(config.api)
user_procces = dict()
config_dir = os.path.join("configs")


params = ["id","full_message"]

@bot.message_handler(commands=['send_test'])
def send_test(message):
    bot.send_message(config.group_chat_pid, "TEST")

######## COMMANDS FOR REMOTE CHATS #########
def is_tagging(message):
    return f'@{bot.get_me().username}' in message.text

def check_author_and_format(message):
    return is_tagging(message) and message.from_user.username in config.users

@bot.message_handler(commands=['get_channel_id_for_chat'], func=lambda message: check_author_and_format(message))
def get_channel_id(message):
    bot.send_message(message.chat.id, f"ID вашего чата: {message.chat.id}",reply_to_message_id=message.message_id)
    bot.send_message(message.chat.id, f"Thread вашего чата: {message.message_thread_id}",reply_to_message_id=message.message_id)
    bot.send_message(message.chat.id, f"Username вашего чата: {message.from_user.username}",reply_to_message_id=message.message_id)

################ MAIN COMMANDS ################

@bot.message_handler(commands=['start'], func=lambda message: check_author_and_format(message))
def start_polling(message):
    if ' group' in message.text:
        print("GROUP STARTED")
        process = start_process(config.group_chat_pid)
    else: process = start_process(message.chat.id)
    if process is None:
        return
    user_procces.update({id: process})
    bot.reply_to(message, f"Запущен! Пид: {str(process.pid)}.")


@bot.message_handler(commands=['kill'], func=lambda message: check_author_and_format(message))
def kill_polling(message):
    pid = user_procces.get(message.chat.id)
    if pid is None:
        bot.send_message(message.chat.id, "Для текущего пользователя проверка не запущена")
        return
    pid.terminate()
    bot.reply_to(message, "Проверка остановлена")
    user_procces.pop(message.chat.id)

@bot.message_handler(commands=["kill_session"], func=lambda message: check_author_and_format(message))
def kill_admin(message):
    if message.chat.id != 1447605962:
        bot.send_message(message.chat.id, "У вас нет прав на использование этой команды")
        return
    try:
        chat = str(message.text).split(" ")[1]
    except:
        bot.send_message(message.chat.id, "Некорректный ввод чата")
    proccess = user_procces.get(int(chat))
    proccess.terminate()
    user_procces.pop(int(chat))
    bot.send_message(message.chat.id, f"Пулл сессия по {chat} удалена")

@bot.message_handler(commands=["status"], func=lambda message: check_author_and_format(message))
def get_status(message):
    pid = user_procces.get(message.chat.id)
    if pid:
        bot.send_message(message.chat.id, "Обнаружена текущая запущенная проверка по PID: " + str(pid.pid))
    else:
        bot.send_message(message.chat.id, "Текущих проверок для пользователя не обнаружено")


@bot.message_handler(commands=["status_all"], func=lambda message: check_author_and_format(message))
def get_all_status(message):
    if not user_procces:
        bot.send_message(message.chat.id, "Текущих проверок не обнаружено")
    else:
        result_message = ""
        for i in user_procces:
            result_message = f"Для чата {i} обнаружена запущенная проверка {(user_procces.get(i)).pid}\n"
        bot.send_message(message.chat.id, result_message)


@bot.message_handler(commands=["config"], func=lambda message: check_author_and_format(message))
def config_polling(message):
    bot.send_message(message.chat.id, '''/config_check @TicketTrackerNTECHbot  - для проверки текущего конфиг\
                                        \n/config_create @TicketTrackerNTECHbot - для создания/пересоздания конфига\
                                        \n/config_info @TicketTrackerNTECHbot param - для получения информации о параметрах конфига\
                                        \n/change_config @TicketTrackerNTECHbot param value - для изменения значения параметра конфига''')


@bot.message_handler(commands=["help"], func=lambda message: check_author_and_format(message))
def help(message):
    bot.send_message(message.chat.id,
                     '''/start @TicketTrackerNTECHbot - запуск экземпляра для уведомлений о новых, неназначенных никому тикетов \
                     \n/kill @TicketTrackerNTECHbot - убить ваш экземпляр уведомлений\n/status @TicketTrackerNTECHbot - получить данные о текущей запущенной \
                     проверке\n/status_all @TicketTrackerNTECHbot - получить данные всех проверках бота\n/help @TicketTrackerNTECHbot - сводка доступных комманд \
                     \n/config @TicketTrackerNTECHbot - раздел конфигурации вашего экземпляра\n''')

############### CHANGE CONFIG #################
@bot.message_handler(commands=["change_config"], func=lambda message: check_author_and_format(message))
def change_config(message):
    if message.text == "/change_config":
        bot.send_message(message.chat.id, "Не указан параметр для изменения")
        return
    try:
        param = str(message.text).split(" ")[2]
        value = str(message.text).split(" ")[3]
    except:
        bot.send_message(message.chat.id, "Данные для изменения введены не корректно")
        return 
    #PARAMS
    if param == "full_message":
        if value == "True":
            replace_line_in_file(str(config_dir) + "/" + str(message.chat.id) + "_config.yaml", "full_message: False", "full_message: True")
        elif value == "False":
            replace_line_in_file(str(config_dir) + "/" + str(message.chat.id) + "_config.yaml", "full_message: True", "full_message: False")
        else:
            bot.send_message(message.chat.id, f"Неверное значение для замены")
        bot.send_message(message.chat.id, f"Значение изменено на {value}")
    if param == "no_reply":
        if value == "True":
            replace_line_in_file(str(config_dir) + "/" + str(message.chat.id) + "_config.yaml", "no_reply: False", "no_reply: True")
        elif value == "False":
            replace_line_in_file(str(config_dir) + "/" + str(message.chat.id) + "_config.yaml", "no_reply: True", "no_reply: False")
        else:
            bot.send_message(message.chat.id, f"Неверное значение для замены")
        bot.send_message(message.chat.id, f"Значение изменено на {value}")
    if param == "reply_time":
        if value.isdigit():
            replace_line_in_file(str(config_dir) + "/" + str(message.chat.id) + "_config.yaml", "reply_time: ", f"reply_time: {value}")
        else: 
            bot.send_message(message.chat.id, f"Значение {value} для данного параметра не корректно")
            return
        bot.send_message(message.chat.id, f"Значение изменено на {value}")
################ INFO CONFIG ##################
@bot.message_handler(commands=["config_info"], func=lambda message: check_author_and_format(message))
def info_config(message):
    if message.text == "/config_info":
        bot.send_message(message.chat.id, "Не указан параметр для информирования")
        return
    elif str(message.text).split( )[2] == "full_message":
        bot.send_message(message.chat.id, '''Параметр отвечает за отправку полной информации в уведомлении о том, что пришел новый тикет. \
                         \nПринимает значения: \n - True : вывод номера, названия, содержания и ссылки на тикет \
                         \n - False : вывод только сообщения о новом тикете''')
    elif str(message.text).split( )[2] == "no_reply":
        bot.send_message(message.chat.id, '''Параметр отвечает за повторную отправку сообщения о тикете, о котором уже оповещалось ранее. \
                         \nПринимает значения: \n - True : Сообщение о новом тикете отправляется единоразово \
                         \n - False : Сообщение о поступившем тикете приходит снова согласно времени установленному в reply_time''')
    elif str(message.text).split( )[2] == "reply_time":
        bot.send_message(message.chat.id, '''Параметр отвечает за частоту опроса youtrack и уведомления пользователя. \
                         \nПринимает значения: \n - Integer : любое число (секунды)''')
################ CHECK CONFIG #################
def check_config(id):
    config_path = f"{config_dir}/{id}_config.yaml"
    try:
        file = open(config_path,"r")
    except:
        return False
    text = file.read()
    file.close()
    for param in params:
        if not param in text:
            return False
    return True

@bot.message_handler(commands=["config_check"], func=lambda message: check_author_and_format(message))
def config_check(message):
    if not (os.path.exists(str(config_dir) + "/" + str(message.chat.id) + "_config.yaml")):
        bot.send_message(message.chat.id, "Конфигурации для текущего пользователя не существует")
        return
    params = dict()
    file = open(str(config_dir) + "/" + str(message.chat.id) + "_config.yaml", "r")
    for line in file:
        line.replace(" ", "")
        param = line.split(":")[0]
        value = str(line.split(":")[1])
        params.update({param: value})
    msg = "Конфигурация для текущего пользователя\n"
    for param in params:
        msg += f"{param} - {params.get(param)}"
    bot.send_message(message.chat.id, msg)
    file.close()

@bot.message_handler(commands=["config_create"], func=lambda message: check_author_and_format(message))
def create_config(message):
    file = open(f"{str(config_dir)}/{str(message.chat.id)}_config.yaml", "w")
    # PLACE FOR NEW PARAMS
    file.write(f"id: {message.chat.id}\n")
    file.write(f"thread: {message.message_thread_id if message.message_thread_id else 'null'}\n")
    file.write(f"full_message: {True}\n")
    file.write(f"no_reply: {True}\n")
    file.write(f"reply_time: {60}")
    # END PARAMS
    file.close()
    bot.send_message(message.chat.id, "Файл конфигурации создан")

################## ALL OTHER ##################
@bot.message_handler(func=lambda message: True)
def start_message(message):
    bot.send_message(message.chat.id, "Список команд /help @TicketTrackerNTECHbot")

def start_process(id):
    if not check_config(id):
        bot.send_message(id, "Конфиграционный файл некорректный или отсуствует, необходимо его пересоздать")
        return None
    process = subprocess.Popen(["python3", "gp-api.py"], stdin=subprocess.PIPE, stderr=subprocess.STDOUT,
                               start_new_session=True)
    process.stdin.write(f"{str(config_dir)}/{str(id)}_config.yaml".encode())
    process.stdin.close()
    return process

def replace_line_in_file(file_path, old_line, new_line):
  try:
    with open(file_path, 'r') as f:
      lines = f.readlines()
    if new_line in lines:
        return
    with open(file_path, 'w') as f:
      for line in lines:
        if line.split(" ")[0] == old_line.split(" ")[0]:
          f.write(new_line + '\n')
        else:
          f.write(line)

    print(f"Строка '{old_line}' успешно заменена на '{new_line}' в файле '{file_path}'")

  except FileNotFoundError:
    print(f"Файл '{file_path}' не найден.")
  except Exception as e:
    print(f"Ошибка при замене строки: {e}")

if __name__ == "__main__":
    bot.polling()
