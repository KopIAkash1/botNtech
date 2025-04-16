import utils.filesAPI as fileAPI
import utils.ticketsAPI as ticketsAPI

from utils.utils import callbacks, cancel
from telebot import types
from loguru import logger

def init_all_callback_handlers(bot):   
    @bot.callback_query_handler(lambda call: call.data == "cancel")
    def cancel_callback_handler(call):
        try:
            global user_to_manage
            user_to_manage = ""
            bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
            bot.answer_callback_query(call.id, "Операция отменена")
            bot.edit_message_text("Операция отменена", chat_id=call.message.chat.id, message_id=call.message.message_id)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        except:
            pass #небольшой похуй)

    @bot.callback_query_handler(lambda call: call.data in callbacks['docs'])
    def docs_callback_handler(call):
        try:
            bot.edit_message_text("Введите номер РР", chat_id=call.message.chat.id, message_id=call.message.message_id)
            global type_of_docs 
            type_of_docs = call.data.split(": ")[1]
            bot.register_next_step_handler(call.message, fileAPI.make_docx_file, type_of_docs, bot)
            logger.info("Started making docx file func")
            bot.answer_callback_query(call.id)
        except Exception as e:
            logger.error(f"Making docs stoped with error {e}") 


    @bot.callback_query_handler(lambda call: "spam" in call.data)
    def spam_callback_handler(call):
        try:
            if "SUP" in call.data:
                logger.info("Sending spam request")
                ticket_id = str(call.data).split(" ")[1]
                ticketsAPI.spam_ticket(ticket_id)
                bot.edit_message_text(chat_id=call.message.chat.id, text=f'Тикет {ticket_id} помечен как спам', message_id=call.message.message_id)
                bot.answer_callback_query(call.id)
        except Exception as e:
            logger.error(f"Getting error in spam logic. Error: {e}")

#Не думаю что будет надобность каждый хендлер оп отдельности регать, но если вдруг надо,
#то понасоздавать тут инит функции с коллбеками и в мейн файле инициализировать 
def init_cancel_handler(bot):
    @bot.callback_query_handler(lambda call: call.data == "cancel")
    def cancel_callback_handler(call):
        try:
            global user_to_manage
            user_to_manage = ""
            bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
            bot.answer_callback_query(call.id, "Операция отменена")
            bot.edit_message_text("Операция отменена", chat_id=call.message.chat.id, message_id=call.message.message_id)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        except:
            pass #небольшой похуй)