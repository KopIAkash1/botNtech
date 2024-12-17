import telebot
import config
import assigneeAPI

bot = telebot.TeleBot(config.api)

@bot.message_handler(commands=["pong"])
def pong(message):
    bot.reply_to(message, "PING")

@bot.message_handler(func= lambda message : "@TicketTrackerNTECHbot" in message.text)
def test(message):
    bot.reply_to(message, "text")

@bot.message_handler(commands=["assignee"])
def assigne_to_user(message):
    tag = ""
    try: 
        print(len(str(message.text).split(" ")))
        if len(str(message.text).split(" ")) >= 3:
            bot.reply_to(message, f"Некорректная команда")
            return
        tag = str(message.text).split(" ")[1]
        print(tag)
    except: print(F"WARNING | Get exception in message. Message: {message.text}")
    name = assigneeAPI.assigne_to_next(tag)
    bot.reply_to(message, f"Переназначение на - {name}")


def is_tagging(message):
    return f'@{bot.get_me().username}' in message.text

def check_author_and_format(message):
    return message.from_user.username in config.users # and is_tagging(message)

@bot.message_handler(commands=['get_channel_id_for_chat'], func=lambda message: check_author_and_format(message))
def get_channel_id(message):
    bot.send_message(message.chat.id, f"ID чата: {message.chat.id}\nThread чата: {message.message_thread_id}",reply_to_message_id=message.message_id)


if __name__ == "__main__":
    bot.polling()