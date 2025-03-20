from loguru import logger
from telebot import types
from utils.utils import check_author_and_format, cancel
from utils.ticketsAPI import get_contents_of_messages
from utils.filesAPI import comments_json_to_doc

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

    @bot.message_handler(commands=['get_comments_doc'], func = lambda message: check_author_and_format(message))
    def make_comments_docx(message):
        params = message.text.split(" ")
        if len(params) != 2:
            bot.send_message(message.chat.id, "Необходимо указать id тикета. Например /get_comments_doc SUP-18000")
            return
        json_path = get_contents_of_messages(params[1])
        document = comments_json_to_doc(json_path)
        bot.send_document(message.chat.id, document)
        document.close()