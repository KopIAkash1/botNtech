import telebot
import subprocess
from telebot import types
import os
import config 

bot = telebot.TeleBot(config.api)
user_procces = dict()


@bot.message_handler(commands=['start'])
def start_polling(message):
    if(message.text == "/start"):
        bot.send_message(message.chat.id, "Для запуска проверки входящих тикетов напиши: /start a.ivanov@ntechlab.com password")
        return
    bot.reply_to(message, "В обработке")
    email = str(message.text).split(" ")[1]
    password = str(message.text).split(" ")[2]
    id = message.chat.id
    pid = start_process(email, password, id)
    user_procces.update({id : pid})
    bot.reply_to(message, f"Запущен! Пид: {str(pid.pid)}. Попытка авторизации.")
	
@bot.message_handler(commands=['kill'])
def kill_polling(message):
	pid = user_procces.get(message.chat.id)
	pid.terminate()
	bot.reply_to(message, "Проверка остановлена")
	user_procces.pop(message.chat.id)

@bot.message_handler(commands=["config"])
def config_polling(message):
    markup=types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1=types.KeyboardButton("Проверить текущий конфиг")
    item2=types.KeyboardButton("Изменить/создать текущий конфиг")
    markup.add(item1, item2)
    bot.send_message(message.chat.id, "Выберите необходимый вариант",reply_markup=markup)

@bot.message_handler(commands=["help"])
def help(message):
	bot.send_message(message.chat.id, f'''/start email password - запуск экземпляра для уведомлений о новых неназначенных никому тикетов\n/kill - убить ваш экземпляр уведомлений\n/help - сводка доступных комманд\n/config - раздел конфигурации вашего экземпляра''')
      
@bot.message_handler(func=lambda message: True)
def start_message(message):
    if(message.text == "Проверить текущий конфиг"):
            if not(os.path.exists(str(message.chat.id) + "_config.yaml")):
                bot.send_message(message.chat.id, "Конфигурации для текущего пользователя не существует")
                return
            params = dict()
            file = open(str(message.chat.id) + "_config.yaml","r")
            for line in file:
                line.replace(" ","")
                param = line.split(":")[0]
                value = str(line.split(":")[1][:-2])
                params.update({param : value})
                print(params)
            msg = "Конфигурация для текущего пользователя"
            for param in params:
                msg += f"\n{param} - {params.get(param)}"
            bot.send_message(message.chat.id, msg)
            file.close()
    elif(message.text == "Изменить/создать текущий конфиг"):
        if not(os.path.exists(str(message.chat.id) + "_config.yaml")):   
                file = open(f"{str(message.chat.id)}_config.yaml","w")
                #Если файла вообще нет его надо создать
                file.write(f"id:{message.chat.id}\n")
                #PLACE FOR NEW PARAMS
                file.close()
                bot.send_message(message.chat.id, "Файл конфигурации создан")
    else:
        bot.send_message(message.chat.id, "Список команд /help")
def start_process(email, password, id):
    process = subprocess.Popen(["python3", "pollingPage.py"], stdin=subprocess.PIPE, stderr=subprocess.STDOUT, start_new_session=True)
    process.stdin.write(f"{email}\n{password}\n{str(id)}\n".encode())
    process.stdin.close()
    return process

if __name__ == "__main__":
	bot.polling()
	
