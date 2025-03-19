from telebot import types
from utils.utils import check_author_and_format, cancel

def init_docs_maker(bot):
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