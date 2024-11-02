import telebot
import subprocess
from telebot import types
import os
import config

bot = telebot.TeleBot(config.api)
user_procces = dict()
config_dir = os.path.join("configs")


params = ["id","full_message"]
################ MAIN COMMANDS ################

@bot.message_handler(commands=['start'])
def start_polling(message):
    if ' group' in message.text and message.chat.id == 1447605962:
        pid = start_process(config.group_chat_pid)
    else: pid = start_process(message.chat.id)
    user_procces.update({id: pid})
    bot.reply_to(message, f"Запущен! Пид: {str(pid.pid)}. Попытка авторизации.")


@bot.message_handler(commands=['kill'])
def kill_polling(message):
    pid = user_procces.get(message.chat.id)
    if pid is None:
        bot.send_message(message.chat.id, "Для текущего пользователя проверка не запущена")
        return
    pid.terminate()
    bot.reply_to(message, "Проверка остановлена")
    user_procces.pop(message.chat.id)

@bot.message_handler(commands=["kill_session"])
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

@bot.message_handler(commands=["status"])
def get_status(message):
    pid = user_procces.get(message.chat.id)
    if pid:
        bot.send_message(message.chat.id, "Обнаружена текущая запущенная проверка по PID: " + str(pid.pid))
    else:
        bot.send_message(message.chat.id, "Текущих проверок для пользователя не обнаружено")


@bot.message_handler(commands=["status_all"])
def get_all_status(message):
    if not user_procces:
        bot.send_message(message.chat.id, "Текущих проверок не обнаружено")
    else:
        result_message = ""
        for i in user_procces:
            result_message = f"Для чата {i} обнаружена запущенная проверка {(user_procces.get(i)).pid}\n"
        bot.send_message(message.chat.id, result_message)


@bot.message_handler(commands=["config"])
def config_polling(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Проверить текущий конфиг")
    item2 = types.KeyboardButton("Создать/пересоздать конфиг")
    item3 = types.KeyboardButton("Изменить текущий конфиг")
    markup.add(item1, item2, item3)
    bot.send_message(message.chat.id, "Выберите необходимый вариант", reply_markup=markup)


@bot.message_handler(commands=["help"])
def help(message):
    bot.send_message(message.chat.id,
                     '''/start email password - запуск экземпляра для уведомлений о новых, неназначенных никому тикетов \
                     \n/kill - убить ваш экземпляр уведомлений\n/status - получить данные о текущей запущенной \
                     проверке\n/status_all - получить данные всех проверках бота\n/help - сводка доступных комманд \
                     \n/config - раздел конфигурации вашего экземпляра\n''')

############### CHANGE CONFIG #################
@bot.message_handler(commands=["change_config"])
def change_config(message):
    if message.text == "/change_config":
        bot.send_message(message.chat.id, "Не указан параметр для изменения")
        return
    try:
        param = str(message.text).split(" ")[1]
        value = str(message.text).split(" ")[2]
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
@bot.message_handler(commands=["config_info"])
def info_config(message):
    if message.text == "/config_info":
        bot.send_message(message.chat.id, "Не указан параметр для информирования")
        return
    elif str(message.text).split( )[1] == "full_message":
        bot.send_message(message.chat.id, '''Параметр отвечает за отправку полной информации в уведомлении о том, что пришел новый тикет. \
                         \nПринимает значения: \n - True : вывод номера, названия, содержания и ссылки на тикет \
                         \n - False : вывод только сообщения о новом тикете''')

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

################## ALL OTHER ##################
@bot.message_handler(func=lambda message: True)
def start_message(message):
    if (message.text == "Проверить текущий конфиг"):
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
    elif (message.text == "Создать/пересоздать конфиг"):
        file = open(f"{str(config_dir)}/{str(message.chat.id)}_config.yaml", "w")
        # PLACE FOR NEW PARAMS
        file.write(f"id: {message.chat.id}\n")
        file.write(f"full_message: {True}\n")
        file.write(f"no_reply: {False}\n")
        file.write(f"reply_time: {5}")
        # END PARAMS
        file.close()
        bot.send_message(message.chat.id, "Файл конфигурации создан")
    elif (message.text == "Изменить текущий конфиг"):
        msg = '''Что бы узнать подробнее о параметрах в конфиге используй команду /config_info. \
                \nСинтаксис: /config_info param(full_message, etc)\
                \nДля изменения значений параметров конфига используй команду /change_config \
                \nСинтаксис: /change_config param(full_message, etc) value(True, False, 5, etc)'''
        bot.send_message(message.chat.id, msg)
    else:
        bot.send_message(message.chat.id, "Список команд /help")

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
