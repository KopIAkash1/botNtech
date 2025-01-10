import telebot
import config
import assigneeAPI

bot = telebot.TeleBot(config.api)

@bot.message_handler(commands=["pong"])
def pong(message):
    bot.reply_to(message, "PING")

@bot.message_handler(commands=["assignee"], func=lambda message: check_author_and_format(message))
def assigne_to_user(message):
    tag = ""
    try: 
        print(len(str(message.text).split(" ")))
        if message.text == "/assignee":
            name = assigneeAPI.assigne_to_next()
            bot.send_message(message.chat.id, f"🖊️Переназначение на основе расписания🖊️\nНазначено: {name}")
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
    return

def is_tagging(message):
    return f'@{bot.get_me().username}' in message.text

def check_author_and_format(message):
    return message.from_user.username in config.users # and is_tagging(message)

@bot.message_handler(commands=['get_channel_id_for_chat'], func=lambda message: check_author_and_format(message))
def get_channel_id(message):
    bot.send_message(message.chat.id, f"ID чата: {message.chat.id}\nThread чата: {message.message_thread_id}",reply_to_message_id=message.message_id)


if __name__ == "__main__":
    bot.polling()