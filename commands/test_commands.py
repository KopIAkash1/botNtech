import telebot, config, random
from utils.utils import check_author_and_format

def init_test_commands(bot):

    @bot.message_handler(commands=["roulette"], func = lambda message: check_author_and_format(message))
    def roulette(message):
        if "l1" in message.text:
            person = config.users[random.randrange(0,4)]
        else:
            person = config.users[random.randrange(5,len(config.users))]
        bot.send_message(message.chat.id, f"Победитель сегодняшней лотерии🎰\n@{person}!\nПоздравляем и/или сочувствуем🫡")

    @bot.message_handler(commands=['get_channel_id_for_chat'], func=lambda message: check_author_and_format(message))
    def get_channel_id(message):
        bot.send_message(message.chat.id, f"ID чата: {message.chat.id}\nThread чата: {message.message_thread_id}",reply_to_message_id=message.message_id)