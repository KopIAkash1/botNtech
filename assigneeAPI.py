import telebot
import requests
import config
import asyncio
import pandas as pd
from datetime import datetime as dt


class Ticket():
    def __init__(self, id, context):
        self.context = context
        self.id = id
        self.url = f"https://tracker.ntechlab.com/tickets/{self.id}"


def read_schedule():
    table = pd.read_excel('./schedule.xlsx', header=None)
    current_user=""
    next_user=""
    current_day = str(dt.now().date())
    current_hour = dt.now().hour
    column = 2
    while True:
        column += 1
        value = str(table.iloc[0,column]).split(" ")[0]
        if value == current_day:
            for i in range(2,8):
                value = str(table.iloc[i, column])
                if value == "9 - 21" and (current_hour >= 9 and current_hour < 21):
                    current_user = table.iloc[i,0]
                    for j in range(i,8):
                        value = str(table.iloc[j, column])
                        if value == "9 - 21":
                            next_user = table.iloc[j,0]
                    return config.name_user[current_user], config.name_user[next_user]
                elif value == "21-9" and (current_hour >= 21 or current_hour <= 9):
                    current_user = table.iloc[i,0]
                    for j in range(2,8):
                        value = str(table.iloc[j, column+1])
                        if value == "9 - 21":
                            next_user = table.iloc[j,0]
                    return config.name_user[current_user], config.name_user[next_user]

def fromate_to_ticket(response):
    tickets = []
    for item in response:
        id = item.get('idReadable')
        summary = item.get('summary')
        tickets.append(Ticket(id,summary))
    return tickets

def get_tickets(name):
    url = f'https://tracker.ntechlab.com/api/issues?fields=id,idReadable,summary,description&query=Assignee: {name} State: -Closed'
    url_headers = {
        'Accept': 'application/json',
        f'Authorization': f'Bearer {config.token}',
        'Content-Type': 'application/json'
    }
    request = requests.get(url, headers=url_headers, verify=False)
    return request.json()



def send_assigne_to_request(json, next_user):
    tickets = fromate_to_ticket(json)
    print(tickets)
    for ticket in tickets:
        request_url = f"https://tracker.ntechlab.com/api/issues/{ticket.id}/fields/159-2506"
        print(request_url)
        url_headers = {
            'Accept': 'application/json',
            f'Authorization': f'Bearer {config.token}',
            'Content-Type': 'application/json'
        }
        data = {
        "id": "159-2506",
        "value": {
            "ringId": f"{config.user_ring_id[next_user]}"
            }
        }
        response = requests.post(request_url, json=data, headers=url_headers, verify=False)

def assigne_to_next(next_user_param : str = ""):
    current_user, next_user = read_schedule()
    if next_user_param != "":
        next_user = next_user_param
    print(f"DEBUT | From - {current_user}")
    print(f"DEBUG | Assignee to - {next_user}")
    tickets = get_tickets(current_user)
    #send_assigne_to_request(tickets, next_user)
    return config.user_tg[next_user]


if __name__ == "__main__":
    assigne_to_next()