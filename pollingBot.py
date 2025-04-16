import telebot
import requests

from loguru import logger
from datetime import datetime
from urllib3 import disable_warnings, exceptions
from config import api, token, group_chat_pid
from time import sleep

disable_warnings(exceptions)

bot = telebot.TeleBot(api)

class Ticket():
    def __init__(self, id, title):
        self.title = title
        self.id = id

def get_page():
    url = 'https://tracker.ntechlab.com/api/issues?fields=idReadable,summary,description&query=project:{Support | Служба поддержки}%20 Assignee: Unassigned State: -Closed, -{Waiting for L2}'
    url_headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    print(type(url_headers))
    request = requests.get(url, headers=url_headers)
    logger.info(f"Request to tickets at {datetime.now()} returned : {request.status_code}")
    return request.json()

def get_tickets_info(json):
    ticketMass = []
    for ticket in json:
        id = ticket['idReadable']
        summary = ticket['summary']
        ticketMass.append(Ticket(id=id, title=summary))
    return ticketMass

def send_message(text):
    markup = telebot.types.InlineKeyboardMarkup()
    button1 = telebot.types.InlineKeyboardButton("Спам", url="https://t.me/TicketTrackerNTECHbot?start=spam_" + text.split("tickets/")[1])
    markup.add(button1)
    bot.send_message(-1001570787209, text, reply_to_message_id=172548, reply_markup=markup)

def polling():
    knwon_tickets = []
    logger.info("Polling started")
    while True:
        json = get_page()
        if len(json) > 0:
            tickets = get_tickets_info(json)
            for ticket in tickets:
                logger.info(f"Find new ticket {ticket.id}")
                if ticket.id not in knwon_tickets: knwon_tickets.append(ticket.id)
                else:
                    continue
                send_message(f'''🟢Новый тикет🟢 \
                        \n{ticket.id}\
                        \nНазвание: {ticket.title}\
                        \nhttps://tracker.ntechlab.com/tickets/{ticket.id}''')
        sleep(300)

if __name__ == "__main__":
    logger.info("Bot started")
    polling()