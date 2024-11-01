from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import telebot
import sys
import config
import yaml


class Settings():
    def __init__(self, config_name):
        with open(config_name) as f:
            params = yaml.safe_load(f)
        self.full_message = params['full_message'] # full message about ticket
        
class Ticket():
    def __init__(self, id, title, context, url):
        self.title = title
        self.context = context
        self.id = id
        self.url = url


url = "https://tracker.ntechlab.com/tickets/search/Unassigned-104?q=project:%20%7BSupport%20%7C%20%D0%A1%D0%BB%D1%83%D0%B6%D0%B1%D0%B0%20%D0%BF%D0%BE%D0%B4%D0%B4%D0%B5%D1%80%D0%B6%D0%BA%D0%B8%7D%20%20Assignee:%20Unassigned%20State:%20-Closed"
bot = telebot.TeleBot(config.api)
email = ""
password = ""


def auth(driver):
    print("Авторизация")
    driver.get("https://tracker.ntechlab.com/hub/auth")
    time.sleep(5)
    login = driver.find_element(By.ID, 'username')
    passfield = driver.find_element(By.ID, 'password')
    login.send_keys(email)
    passfield.send_keys(password)
    driver.find_element(By.CLASS_NAME, "auth-button_wide").click()
    time.sleep(5)

def getPage(driver, settings):
    driver.get(url)
    time.sleep(5)
    checkError = driver.find_elements(By.CLASS_NAME, 'error__f068')
    #print(checkError)
    if(checkError == []):
        if not settings.full_message:
            bot.send_message(id, "🟢Новый тикет🟢")
            return
        ticket = get_ticket_info(driver)
        msg = f'''🟢Новые тикеты:🟢 \
                \n{ticket.id}\
                \nНазвание: {ticket.title}\
                \nСодержание: {ticket.context}\
                \n{ticket.url}'''
        bot.send_message(id, msg)
        return
    #print("No new tickets at " + str(time.strftime("%H:%M:%S", time.localtime())))
    #bot.send_message(1447605962, "Новый тикет НЕ пришел")

def get_ticket_info(driver):
    ticket_div = driver.find_element(By.CLASS_NAME, 'summary__b71b')
    title = ticket_div.get_attribute("aria-label")
    ticket_url = (ticket_div.find_element(By.XPATH, './/a')).get_attribute('href')
    id = ticket_url.split('/')[4]
    driver.get(ticket_url)
    time.sleep(5)
    context_mass = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/div/div/div/div/div/article/div/div/div/div[2]/section/div/div[1]/div')
    context_paragraphs = context_mass.find_elements(By.XPATH, './/p')
    context = ''
    for par in context_paragraphs:
        context += par.text
    return Ticket(id=id,title=title,context=context,url=ticket_url)
    
def startPolling(settings):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_service = Service(executable_path="./chromedriver")
    driver = webdriver.Chrome(service=chrome_service , options=chrome_options)
    print("DRIVER STARTED")
    auth(driver)
    bot.send_message(id, "Авторизация пройдена")
    while True:
        getPage(driver, settings)
        time.sleep(30)

if __name__ == "__main__":
    email = sys.stdin.readline().strip()
    password = sys.stdin.readline().strip()
    id = int(sys.stdin.readline().strip())
    settings = Settings(sys.stdin.readline().strip())
    print("STARTED SESSION")
    startPolling(settings)
