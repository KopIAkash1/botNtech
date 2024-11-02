import requests
import config


class Ticket():
    def __init__(self, id, title, context, url):
        self.title = title
        self.context = context
        self.id = id
        self.url = url


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


if __name__ == '__main__':
    a = get_page()
    get_ticket_info(a)
    print(1)
