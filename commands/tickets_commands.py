import config
import utils.db as db
import utils.ticketsAPI as ticketsAPI

from utils.filesAPI import make_html_file
from utils.utils import check_author_and_format, callbacks, cancel
from telebot import types
from loguru import logger

def init_manage_access_command(bot):
    #Небольшое исключение изза register_next_step_handler
    @bot.callback_query_handler(lambda call: call.data in callbacks['manage_access'])
    def manage_access_callback_handler(call):
        try:
            if call.data == "add":
                markup_second = types.InlineKeyboardMarkup()
                markup_second.add(cancel)
                bot.edit_message_text("Введите тикеты, к которым требуется выдать доступ", call.message.chat.id, call.message.message_id)
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup_second)
                bot.register_next_step_handler(call.message, manage_access_to_view_ticket_add)
            elif call.data == "remove":
                markup_second = types.InlineKeyboardMarkup()
                markup_second.add(cancel)
                bot.edit_message_text("Введите тикеты, к которым требуется забрать доступ", call.message.chat.id, call.message.message_id)
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup_second)
                bot.register_next_step_handler(call.message, manage_access_to_view_ticket_rem)
        except Exception as e:
            logger.error(f"Something gone wrong with error {e}")
    
    @bot.message_handler(commands=["manage_access"], func=lambda message: check_author_and_format(message))
    def manage_access_to_view_ticket(message):
        markup = types.InlineKeyboardMarkup()
        markup.add(cancel)
        bot.send_message(message.chat.id, text="Укажите ID пользователя в Телеграм", reply_markup=markup)
        bot.register_next_step_handler(message, manage_access_to_view_ticket_follow_up)
    
    def manage_access_to_view_ticket_follow_up(message):
        markup = types.InlineKeyboardMarkup()
        markup.add(cancel)
        if len(message.text.strip().split(" ")) > 1:
            bot.send_message(message.chat.id, text="Укажите одного пользователя",reply_markup=markup)
            bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
            bot.register_next_step_handler(message, manage_access_to_view_ticket_follow_up)
        else:
            if message.text.startswith("@"): message.text = message.text[1:]
            global user_to_manage
            user_to_manage = message.text.lower()
            markup = types.InlineKeyboardMarkup()
            markup_but1 = types.InlineKeyboardButton("Добавить доступ к тикету", callback_data="add")
            markup_but2 = types.InlineKeyboardButton("Удалить доступ к тикету", callback_data="remove")
            markup.row(markup_but1, markup_but2)
            markup.row(cancel)
            bot.send_message(message.chat.id, text="Выберите опцию", reply_markup=markup)
    
    def manage_access_to_view_ticket_add(message):
        global user_to_manage
        tickets = message.text.strip().split(" ")
        error = []
        goods = []
        for ticket in tickets:
            ticket.strip()
            if not ticket.upper().startswith("SUP-"): error.append(ticket)
            elif len(ticket) != 9: error.append(ticket)
            else: goods.append(ticket.upper())
        error = [err for err in error if err.strip()]
        goods = [good for good in goods if good.strip()]
        goods = list(dict.fromkeys(goods))
        result = ""
        try: db.set_tickets_to_user(user_to_manage, " ".join(goods))
        except Exception as e:
            user_to_manage = ""
            logger.error(e)
        user_to_manage = ""
        if len(error) > 0:
            result += "*Ошибка при обработке тикетов*: \n" + ", ".join(error) + "\n\n"
        if len(goods) > 0: result += "*Успешно добавленные тикеты*: \n" + ", ".join(goods)
        bot.send_message(message.chat.id, parse_mode="Markdown", text=result)

    #TODO: Доделать функцию для удаления тикетов в базе, начать делать запрос тикета по номеру, расскоментить хендлер на rem
    def manage_access_to_view_ticket_rem(message):
        global user_to_manage
        tickets = message.text.strip().split(" ")
        error = []
        goods = []
        for ticket in tickets:
            ticket.strip()
            if not ticket.upper().startswith("SUP-"): error.append(ticket)
            elif len(ticket) != 9: error.append(ticket)
            else: goods.append(ticket.upper())
        error = [err for err in error if err.strip()]
        goods = [good for good in goods if good.strip()]
        goods = list(dict.fromkeys(goods))
        result = ""
        try: 
            db.rem_tickets_from_user(user_to_manage, " ".join(goods))
        except Exception as e:
            user_to_manage = ""
            logger.error(e)
        else:
            user_to_manage = ""
            if len(error) > 0:
                result += "*Ошибка при обработке тикетов*: \n" + ", ".join(error) + "\n\n"
            if len(goods) > 0: result += "*Успешно удаленные тикеты*: \n" + ", ".join(goods)
            bot.send_message(message.chat.id, parse_mode="Markdown", text=result)

def init_tickets_managment_commands(bot):
    @bot.message_handler(commands=['get_comments_json'], func= lambda message: check_author_and_format(message))
    def get_comments_json(message):
        #TODO: если у пользователя есть права
        if len(str(message.text).split(" ")) != 2:
            bot.send_message(message.chat.id, "Необходимо указать id тикета. Например /get_comments_json SUP-18000")
            return
        number = str(message.text).split(" ")[1]
        json_path = ticketsAPI.get_contents_of_messages(number)
        if not(json_path):
            bot.send_message(message.chat.id, "Тикет с данным номером найти не удалось или возникла ошибка")
            return
        file = open(json_path, 'rb')
        bot.send_document(message.chat.id, file)
        file.close()

    #TODO: Заменить лямбду на другую, которая будет чекать по бд людей с доступом, а не по конфигу 
    @bot.message_handler(commands=['get_comments_html'], func= lambda message: check_author_and_format(message))
    def get_comments_html(message):
        if len(str(message.text).split(" ")) != 2:
            bot.send_message(message.chat.id, "Необходимо указать id тикета. Например `/get_comments_html SUP-18000`")
            return
        number = str(message.text).split(" ")[1]
        json_path = ticketsAPI.get_contents_of_messages(number)
        if not(json_path):
            bot.send_message(message.chat.id, "Тикет с данным номером найти не удалось или возникла ошибка")
            return
        try:
            html_path = make_html_file(json_path)
            file = open(html_path, 'rb')
            bot.send_document(message.chat.id, file)
            file.close()
        except Exception as e:
            logger.error(e)
            return
        
        
    
    @bot.message_handler(commands=['tickets_count'], func= lambda message : check_author_and_format(message))
    def get_tickets_count(message):
        try:
            logger.info(f"Get request for count tickets by {message.from_user.username}")
            current_user, _ = ticketsAPI.read_schedule()
            tickets = ticketsAPI.get_tickets(current_user)
            logger.info(f"Get {len(tickets)} tickets")
            bot.send_message(message.chat.id, f"На данный момент на первой линии всего {len(tickets)} тикетов")
        except Exception as e:
            logger.error(f"Something gone wrong with error: {e}")

    @bot.message_handler(commands=["assignee"], func=lambda message: check_author_and_format(message))
    def assigne_to_user(message):
        global assignee_from_group
        logger.info(f"Started assignee func by {message.from_user.username}")
        message.text = message.text.replace("start ","")    
        try: 
            print(len(str(message.text).split(" ")))
            current_user, next_user = ticketsAPI.read_schedule()
            print(f"Message get from @{message.from_user.username} and current_user by schedule is {current_user} and next user is {next_user}")
            if message.text == "/assignee":
                if f"@{message.from_user.username}" == config.user_tg[current_user] or f"@{message.from_user.username}" == config.user_tg[next_user]:
                    if not(assignee_from_group):
                        name = ticketsAPI.assigne_to_next()
                        bot.send_message(message.chat.id, f"🖊️Переназначение на основе расписания🖊️\nНазначено: {name}")
                        assignee_from_group = True
                        logger.info(f"Assignee from {current_user} to {next_user}")
                    else:
                        print(f"Already assigned")
                else:
                    print("User are not allowed to assignee")
            elif len(message.text.split(" ")) == 2:
                next_user = message.text.split(" ")[1]
                name = ticketsAPI.assigne_to_next(next_user_param=next_user)
                bot.send_message(message.chat.id, f"📎Переназначение на конкретного пользователя📎\nНазначено:{name}")
            elif len(message.text.split(" ")) == 3:
                old_user = message.text.split(" ")[1]
                next_user = message.text.split(" ")[2]
                name = ticketsAPI.assigne_to_next(old_user_param=old_user, next_user_param=next_user)
                bot.send_message(message.chat.id, f"🤝Переназначение с одного на другого пользователя🤝\nТикеты с {old_user}\nНазначены на {next_user}")
        except Exception as e: print(F"WARNING | Get exception in message. Message: {message.text}\n{e}")

        @bot.message_handler(commands=["start"])
        def start(message):
            if "assignee" in message.text:
                assigne_to_user(message)
            elif "spam" in message.text:
                logger.info("Sending spam request")
                ticket_id = message.text.split("_")[1]
                ticketsAPI.spam_ticket(ticket_id)
                bot.send_message(message.chat.id, f"Тикет {ticket_id} помечен как спам")