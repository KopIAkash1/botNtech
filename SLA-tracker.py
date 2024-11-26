import config
import requests
import time
import telebot
from datetime import datetime

bot = telebot.TeleBot(config.api)

user_and_next_user = {
     #первый из передачи после дневной, второй после ночной
    'a.aleksandrov' : {'i.frolov@ntechlab.com', 'a.tolstopyat@ntechlab.com'},
    'a.tolstopyat@ntechlab.com' : {'d.kalinin@ntechlab.com', 'i.frolov@ntechlab.com'},
    'a.provotorov@ntechlab.com' : {'a.tolstopyat@ntechlab.com', 'a.aleksandrov'},
    'd.kalinin@ntechlab.com' : {'a.aleksandrov', 'a.provotorov@ntechlab.com'},
    'i.frolov@ntechlab.com' : {'a.provotorov@ntechlab.com', 'd.kalinin@ntechlab.com'}
}

user_tg = {
    'a.aleksandrov' : '@Shiretomi',
    'a.tolstopyat@ntechlab.com' : '@Kopi150',
    'a.provotorov@ntechlab.com' : '@AlexeyPR8',
    'd.kalinin@ntechlab.com' : '@difoxevith',
    'i.frolov@ntechlab.com' : '@Rusha1227'
}
current_user = list(user_and_next_user.keys())[config.SLA_shift - 1]
switch_completed = False
known_tickets = []

class Ticket:
    def __init__(self, id, summary, current_time_till_sla):
        self.id = id
        self.summary = summary
        self.sla_state = current_time_till_sla > datetime.timestamp(datetime.now())

def get_current_tasks():
    url = 'https://tracker.ntechlab.com/api/issues?fields=idReadable,summary,fields(value)&query=project:{Support | Служба поддержки}%20 Assignee:' + current_user + ' State: -Closed, -{Waiting for L2}, -{Waiting for delivery}, -{Waiting for developer}, -{On hold}' 
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
                    \n{user_tg[current_user]}'''
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
        if datetime.now().hour == 21 and not switch_completed:
            switch_user(to_night=True)
            switch_completed = True
        elif datetime.now().hour == 9 and not switch_completed:
            switch_user(to_night=False)
            switch_completed = True
        elif datetime.now().hour != 21 and datetime.now().hour != 9:
            switch_completed = False
        get_known_tickets()
        response = get_current_tasks()
        tickets = fromate_to_ticket(response)
        send_SLA_break_message(tickets)
        time.sleep(300)


if __name__ == "__main__":
    print(f"[DEBUG] | Current user : {current_user}")
    polling()
