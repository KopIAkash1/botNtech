from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import telebot
import sys
import config

url = "https://tracker.ntechlab.com/tickets/search/Unassigned-104?q=project:%20%7BSupport%20%7C%20%D0%A1%D0%BB%D1%83%D0%B6%D0%B1%D0%B0%20%D0%BF%D0%BE%D0%B4%D0%B4%D0%B5%D1%80%D0%B6%D0%BA%D0%B8%7D%20%20Assignee:%20Unassigned%20State:%20-Closed"
bot = telebot.TeleBot(config.api)
email = ""
password = ""
id = -1
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

def getPage(driver):
    driver.get(url)
    time.sleep(5)
    checkError = driver.find_elements(By.CLASS_NAME, 'error__f068')
    #print(checkError)
    if(checkError == []):
        print("Find new one")
        bot.send_message(id, "Новый тикет пришел")
        return
    #print("No new tickets at " + str(time.strftime("%H:%M:%S", time.localtime())))
    #bot.send_message(1447605962, "Новый тикет НЕ пришел")
    return

def startPolling():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    auth(driver)
    bot.send_message(id, "Авторизация пройдена")
    while True:
        getPage(driver)
        time.sleep(30)
if __name__ == "__main__":
    email = sys.stdin.readline().strip()
    password = sys.stdin.readline().strip()
    id = int(sys.stdin.readline().strip())
    #print(sys.argv[1],sys.argv[2],sys.argv[3])
    startPolling()