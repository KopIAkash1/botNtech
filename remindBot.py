import config
import telebot

from time import sleep
from datetime import datetime
from utils.ticketsAPI import send_change_request_ticket
from loguru import logger
from utils.db import get_all_remind_tickets, remove_remind_ticket

bot = telebot.TeleBot(config.api)

def remindCycle():
    while True:
        tickets = get_all_remind_tickets()
        for ticket in tickets:
            if int(datetime.now().timestamp()) > ticket[1]:
                logger.info(f"Finding ticket {ticket[0]} with needs in reminding")
                data = {"id": "158-10165","event": {"id": "waiting for support"}}
                send_change_request_ticket(ticket_id=ticket[0], data=data, field="158-10165")
                logger.info("Request sended")
                if remove_remind_ticket(ticket[0]):
                    logger.info(f"Ticket with id {ticket[0]} successfully deleted from db")
                else:
                    logger.warning(f"Cannot delete ticket with id {ticket[0]}. Maybe already deleted")
        sleep(5)

if __name__ == "__main__":
    remindCycle()