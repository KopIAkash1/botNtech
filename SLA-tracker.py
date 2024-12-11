import config
import requests
import time
import telebot
from datetime import datetime
import pandas as pd
import logging as log

bot = telebot.TeleBot(config.api)
switch_completed = False
known_tickets = []
current_user = ""

class Ticket:
    def __init__(self, id, summary, current_time_till_sla):
        self.id = id
        self.summary = summary
        self.sla_state = current_time_till_sla > datetime.timestamp(datetime.now())


def read_schedule():
    table = pd.read_excel('./schedule.xlsx', header=None)
    current_day = str(datetime.now().date())
    current_hour = datetime.now().hour
    column = 3
    while True:
        value = str(table.iloc[0,column]).split(" ")[0]
        column += 1
        if value == current_day:
            for i in range(2,6):
                value = str(table.iloc[i, column])
                if value == "9 - 21" and (current_hour >= 9 and current_hour <= 21):
                    current_user = table.iloc[i-1,0]
                    return config.name_user[current_user]
                elif value == "21-9" and (current_hour >= 21 or current_hour <= 9):
                    current_hour = table.iloc[i-1,0]
                    return config.name_user[current_user]

def get_current_tasks():
    url = 'https://tracker.ntechlab.com/api/issues?fields=idReadable,summary,fields(value)&query=State:%20%7BWaiting%20for%20support%7D%20,%20%7BWaiting%20for%20customer%7D%20%20State:%20-Closed%20Project:%20%7BSupport%20%7C%20Служба%20поддержки%7D%20' 
    url_headers = {
        'Accept': 'application/json',
        f'Authorization': f'Bearer {config.token}',
        'Content-Type': 'application/json'
    }
    request = requests.get(url, headers=url_headers, verify=False)
    return request.json()

def fromate_to_ticket(response):
    tickets = []
    for item in response:
        id = item.get('idReadable')
        summary = item.get('summary')
        SLA_time = item.get("fields", [{}])[0].get("value", None)
        if isinstance(SLA_time, int): tickets.append(Ticket(id,summary,SLA_time))
    return tickets

def send_SLA_break_message(tickets):
    global current_user
    global switch_completed
    with open('sla_broken_tickets.txt', 'a') as known_tickets_file:
        for ticket in tickets:
            if ticket.id in known_tickets: continue
            elif (ticket.sla_state):
                msg = f'''🔴Истек срок решения🔴\
                    \n{ticket.id}\
                    \nSummary: {ticket.summary}\
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

def switch_user(to_night):
    global current_user
    global switch_completed
    global user_and_next_user
    current_user = list(user_and_next_user[current_user])[1 if to_night else 0]
    print(f"[DEBUG] | Current user changed to : {current_user}")

def polling():
    global current_user
    global switch_completed
    while True:
        get_known_tickets()
        response = get_current_tasks()
        tickets = fromate_to_ticket(response)
        send_SLA_break_message(tickets)
        time.sleep(600)


if __name__ == "__main__":
    current_user = read_schedule()
    print(f"[DEBUG] | Current user : {current_user}")
    polling()
