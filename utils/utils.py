import config
from telebot import types

cancel = types.InlineKeyboardButton("Отмена", callback_data="cancel")

callbacks = {
    'docs': ["doc_type: 1", "doc_type: 2", "doc_type: 3"],
    'manage_access': ["add", "remove", "remove_user"],
}

def check_author_and_format(message):
    return message.from_user.username in config.users