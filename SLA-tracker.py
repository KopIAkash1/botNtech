import config
import telebot
import urllib3
import utils.ticketsAPI as ticketAPI
import utils.filesAPI as filesAPI
import time

from loguru import logger

bot = telebot.TeleBot(config.api)
known_tickets = []
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def send_SLA_break_message(tickets):
    global current_user
    global switch_completed
    with open('sla_broken_tickets.txt', 'a') as known_tickets_file:
        for ticket in tickets:
            if ticket.id in known_tickets: continue
            elif (ticket.sla_state == False):
                msg = f'''🔴Истек срок решения🔴\
                    \n{ticket.id}\
                    \n{ticket.context}\
                    \nhttps://tracker.ntechlab.com/tickets/{ticket.id}\
                    \n{config.user_tg[current_user]}'''
                known_tickets_file.write(f"{ticket.id}\n")
                bot.send_message(chat_id=1447605962, text = msg, reply_to_message_id=0)
        known_tickets_file.close()

def get_known_tickets():
    with open("sla_broken_tickets.txt", "r") as known_tickets_file:
        for line in known_tickets_file:
            if line != "":
                known_tickets.append(line[:-1])
        known_tickets_file.close()

def polling():
    current_user = ''
    global switch_completed
    while True:
        get_known_tickets()
        current_user, _ = filesAPI.read_schedule()
        logger.info(f"Current user for check is: {current_user}")
        response = ticketAPI.get_tickets(current_user)
        tickets = ticketAPI.fromate_to_ticket(response)
        logger.info(f"Get {len(tickets)} for user {current_user}")
        send_SLA_break_message(tickets)
        time.sleep(600)

if __name__ == "__main__":
    polling()
