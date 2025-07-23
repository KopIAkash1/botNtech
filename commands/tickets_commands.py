import config
import utils.db as db
import utils.ticketsAPI as ticketsAPI

from utils.filesAPI import make_html_file
from utils.utils import check_author_and_format, callbacks, cancel
from telebot import types
from loguru import logger
from datetime import datetime

assignee_from_group = False

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
            bot.send_message(message.chat.id, "Необходимо указать id тикета. Например /get_comments_json SUP-18000", reply_to_message_id=message.id)
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
    @bot.message_handler(commands=['get_comments_html'])
    def get_comments_html(message):
        if len(str(message.text).split(" ")) != 2:
            bot.send_message(message.chat.id, "Необходимо указать id тикета. Например `/get_comments_html SUP-18000`" ,reply_to_message_id = message.id)
            return
        number = str(message.text).split(" ")[1]
        if message.from_user.username in config.users: pass
        elif db.is_user_exist(message.from_user.username.lower()): 
            try:
                tickets = db.get_tickets_by_user(message.from_user.username.lower())
                tickets = tickets.split(" ")
                if number.upper() in tickets: pass
                else: 
                    bot.send_message(message.chat.id, "Нет доступа к тикету", reply_to_message_id=message.id)
                    return
            except Exception as e:
                logger.error(e)
        else: 
            bot.send_message(message.chat.id, "Нет прав")
            return
        json_path = ticketsAPI.get_contents_of_messages(number)
        if not(json_path):
            bot.send_message(message.chat.id, "Тикет с данным номером найти не удалось или возникла ошибка", reply_to_message_id=message.id)
            return
        try:
            html_path = make_html_file(json_path)
            file = open(html_path, 'rb')
            bot.send_document(message.chat.id, file, reply_to_message_id=message.id)
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
            bot.send_message(message.chat.id, f"На данный момент на первой линии всего {len(tickets)} тикетов", reply_to_message_id = message.id)
        except Exception as e:
            logger.error(f"Something gone wrong with error: {e}")
    
    @bot.message_handler(commands=["tickets_list"])
    def get_tickets_list(message):
        target_user = ''
        if len(message.text.split(" ")) == 2:
            target_user = config.tg_user[message.text.split(" ")[1]]
        try: 
            logger.info("Getting tickets list...")
            if target_user == '': target_user, _ = ticketsAPI.read_schedule()
            tickets = ticketsAPI.fromate_to_ticket(ticketsAPI.get_tickets(target_user))
            logger.info(f"Get {len(tickets)} tickets")
            text = ''
            for ticket in tickets:
                id = ticket.id
                context = ticket.context
                text += f'{id} - {context}\n'
            bot.send_message(message.chat.id, text, reply_to_message_id=message.id)
        except Exception as e:
            logger.error(f"Something gone wrong with error: {e}")

    @bot.message_handler(commands=["assignee"], func=lambda message: check_author_and_format(message))
    def assigne_to_user(message):
        global assignee_from_group
        logger.info(f"Started assignee func by {message.from_user.username}")
        message.text = message.text.replace("start ","")    
        try: 
            current_user, next_user = ticketsAPI.read_schedule()
            logger.info(f"Message get from @{message.from_user.username} and current_user by schedule is {current_user} and next user is {next_user}")
            if message.text == "/assignee":
                if f"@{message.from_user.username}" == config.user_tg[current_user] or f"@{message.from_user.username}" == config.user_tg[next_user]:
                    if not(assignee_from_group):
                        logger.info("Starting assignee by schedule...")
                        name = ticketsAPI.assigne_to_next()
                        bot.send_message(message.chat.id, f"🖊️Переназначение на основе расписания🖊️\nНазначено: {name}", reply_to_message_id = message.id)
                        assignee_from_group = True
                        logger.info(f"Assignee from {current_user} to {next_user}")
                    else:
                        logger.info(f"Already assigned")
                else:
                    logger.info("User are not allowed to assignee")
            elif len(message.text.split(" ")) == 2:
                next_user = message.text.split(" ")[1]
                name = ticketsAPI.assigne_to_next(next_user_param=next_user)
                bot.send_message(message.chat.id, f"📎Переназначение на конкретного пользователя📎\nНазначено:{name}", reply_to_message_id = message.id)
            elif len(message.text.split(" ")) == 3:
                old_user = message.text.split(" ")[1]
                next_user = message.text.split(" ")[2]
                name = ticketsAPI.assigne_to_next(old_user_param=old_user, next_user_param=next_user)
                bot.send_message(message.chat.id, f"🤝Переназначение с одного на другого пользователя🤝\nТикеты с {old_user}\nНазначены на {next_user}", reply_to_message_id = message.id)
        except Exception as e: logger.info(F"WARNING | Get exception in message. Message: {message.text}\n{e}")

    @bot.message_handler(commands=["remind"])
    def remind_command(message):
        params = message.text.split(" ")
        logger.info("Starting remind method")
        if len(params) == 3:
            ticket_id = params[1]
            seconds = int(datetime.now().timestamp()) + int(params[2])
            data = {"id": "158-10165","event": {"id": "waiting for customer"}}
            ticketsAPI.send_change_request_ticket(ticket_id=ticket_id, data=data, field="158-10165")
            db.set_ticket_remind_time(ticket_id, seconds)
            logger.info(f"Ticket {ticket_id} successfully added to remind at {seconds}")
            bot.send_message(message.chat.id, f"Тикет {ticket_id} добавлен в ожидание до {datetime.fromtimestamp(seconds)}", reply_to_message_id = message.id)
        else:
            bot.send_message(message.chat.id, "/remind <Ticket-Id> <seconds>", reply_to_message_id = message.id)

    @bot.message_handler(commands=["get_remind_ticket"])
    def get_remind_ticket_command(message):
        logger.debug(f"ADMIN TOOL | get_remind_ticket info used by {message.from_user.username}")
        ticket_id = message.text.split(" ")[1]
        answer = db.get_ticket_remind_time(ticket_id)
        if not answer: 
            bot.send_message(message.chat.id, f"Не удалось найти отложенный тикет с айди {ticket_id}", reply_to_message_id = message.id)
            return
        bot.send_message(message.chat.id, f"{answer[0]} {datetime.fromtimestamp(answer[1])}", reply_to_message_id = message.id)

    @bot.message_handler(commands=["remove_remind_ticket"])
    def remove_remind_ticket_command(message):
        logger.debug(f"ADMIN TOOL | remove_remind_ticket info used by {message.from_user.username}")
        ticket_id = message.text.split(" ")[1]
        answer = db.__remove_remind_ticket(ticket_id)
        logger.debug(f"Trying to delete ticket with id {ticket_id}...")
        if answer:
            logger.debug(f"Deleted successefully")
            bot.send_message(message.chat.id, f"{ticket_id} удален из напоминаний", reply_to_message_id = message.id)
        else:
            logger.warning(f"Deleted failed")
            bot.send_message(message.chat.id, f"{ticket_id} найти не удалось или он уже удален", reply_to_message_id = message.id)

    @bot.message_handler(commands=["start"])
    def start(message):
        if "assignee" in message.text:
            assigne_to_user(message)
        elif "spam" in message.text:
            ticket_id = message.text.split("_")[1]
            button1 = types.InlineKeyboardButton("Да", callback_data=f"spam {ticket_id}")
            button2 = types.InlineKeyboardButton("Нет", callback_data=f"not spam {ticket_id}")
            markup = types.InlineKeyboardMarkup()
            markup.add(button1)
            markup.add(button2)
            bot.send_message(message.chat.id, f"Вы уверены, что хотите пометить тикет {ticket_id} как спам?", reply_markup=markup)

    