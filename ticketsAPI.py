import requests
import config
import pandas as pd
import urllib3

from filesAPI import read_schedule
from loguru import logger
from datetime import datetime as dt

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Ticket():
    def __init__(self, id, context):
        self.context = context
        self.id = id
        self.url = f"https://tracker.ntechlab.com/tickets/{self.id}"

def fromate_to_ticket(response):
    tickets = []
    for item in response:
        id = item.get('idReadable')
        summary = item.get('summary')
        tickets.append(Ticket(id,summary))
    return tickets

def get_tickets(name):
    url = f'https://tracker.ntechlab.com/api/issues?fields=id,idReadable,summary,description&query=Assignee: {name} State: -Closed'
    logger.debug(f"[DEBUG] making request to get tickets: {url}")
    url_headers = {
        'Accept': 'application/json',
        f'Authorization': f'Bearer {config.token}',
        'Content-Type': 'application/json'
    }
    request = requests.get(url=url, headers=url_headers, verify=False)
    #print(request.text)
    return request.json()



def send_assigne_to_request(json, next_user):
    tickets = fromate_to_ticket(json)
    print(f"Count of tikcets: {len(tickets)}")
    for ticket in tickets:
        request_url = f"https://tracker.ntechlab.com/api/issues/{ticket.id}/fields/159-2506"
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
        print(f"Trying send request to assignee on ticket: {ticket.id}")
        response = requests.post(request_url, json=data, headers=url_headers, verify=False)
        print(f"Get result: {response.status_code, response.text}")

def assigne_to_next(old_user_param : str = "",next_user_param : str = "") -> str:
    current_user, next_user = read_schedule()
    if next_user_param != "":
        next_user = config.tg_user[next_user_param]
    if old_user_param != "":
        current_user = config.tg_user[old_user_param]
    print(f"DEBUG | From - {current_user}")
    print(f"DEBUG | Assignee to - {next_user}")
    tickets = get_tickets(current_user)
    #send_assigne_to_request(tickets, next_user)
    return config.user_tg[next_user]

def send_change_request_ticket(ticket_id, data, field):
    url = f"https://tracker.ntechlab.com/api/issues/{ticket_id}/fields/{field}"
    url_headers = {
        'Accept': 'application/json',
        f'Authorization': f'Bearer {config.token}',
        'Content-Type': 'application/json'
    }
    response = requests.post(url, json=data, headers=url_headers, verify=False)
    return response.status_code, response.text

def spam_ticket(ticket_id):
    current_user, _ = read_schedule()

    data = { "id": "159-2506", "value": {"ringId": f"{config.user_ring_id[current_user]}" } }
    status, text = send_change_request_ticket(ticket_id, data, "159-2506")
    print(f"DEBUG | Send request to assignee on ticket: {ticket_id} | {status, text}")

    data = {"id": "158-10832","value": {"description": f"","id": "138-5442", "kind": "enum","label": "Спам","name": "Спам"}}
    status, text = send_change_request_ticket(ticket_id, data, "158-10832")
    print(f"DEBUG | Send request to customer on ticket: {ticket_id} | {status, text}")
    
    data = {"id": "517-16752","value": f"Спам"}
    status, text = send_change_request_ticket(ticket_id, data, "517-16752")
    print(f"DEBUG | Send request to solution on ticket: {ticket_id} | {status, text}")

    data = {"id": "158-10166","value": [{"description": None,"id": "166-796","kind": "enum","label": "Spam","name": "Spam"}]}
    status, text = send_change_request_ticket(ticket_id, data, "158-10166")
    print(f"DEBUG | Send request to subsystem on ticket: {ticket_id} | {status, text}")

    data = {"id": "158-10165","event": {"id": "resolved"}}
    status, text = send_change_request_ticket(ticket_id, data, "158-10165")
    print(f"DEBUG | Send request to state on ticket: {ticket_id} | {status, text}")

    data = {"id": "158-10165","event": {"id": "closed"}}
    status, text = send_change_request_ticket(ticket_id, data, "158-10165")
    print(f"DEBUG | Send request to state on ticket: {ticket_id} | {status, text}")

    print("END OF SENDING REQUESTS")

if __name__ == "__main__":
    assigne_to_next()