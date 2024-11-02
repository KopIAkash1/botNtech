import requests
import config
import yaml
import sys
import telebot
import time

bot = telebot.TeleBot(config.api)

class Ticket():
    def __init__(self, id, title, context, url):
        self.title = title
        self.context = context
        self.id = id
        self.url = url

class Settings():
    def __init__(self, config_name):
        with open(config_name) as f:
            params = yaml.safe_load(f)
        self.id = params['id'] # user's chat id
        self.full_message = params['full_message'] # full message about ticket

def get_page():
    url = 'https://tracker.ntechlab.com/api/issues?fields=idReadable,summary,description&query=project:{Support | Служба поддержки}%20 Assignee: me State: +Closed&sort=state'
    url_headers = {
        'Accept': 'application/json',
        f'Authorization': f'Bearer {config.token}',
        'Content-Type': 'application/json'
    }
    request = requests.get(url, headers=url_headers)
    return request.json()


def get_ticket_info(json):
    id = json[0]['idReadable']
    summary = json[0]['summary']
    desc = json[0]['description']
    url = f"https://tracker.ntechlab.com/tickets/{id}/{summary}"
    return Ticket(id=id, title=summary, context=desc, url=url)

def polling(settings):
    print("POLLING STARTED")
    while True:
        answer = get_page()
        if len(answer) > 0:
            ticket = get_ticket_info(answer)
            if settings.full_message:
                send_message(f'''🟢Новы тикет:🟢 \
                \n{ticket.id}\
                \nНазвание: {ticket.title}\
                \nСодержание: {ticket.context}\
                \n{ticket.url}''',settings)
            else:
                send_message("🟢Новый тикет🟢",settings)
        time.sleep(15)

def send_message(msg, settings):
    bot.send_message(settings.id, msg)

if __name__ == '__main__':
    settings = Settings(sys.stdin.readline().strip())
    polling(settings)
    print(1)
