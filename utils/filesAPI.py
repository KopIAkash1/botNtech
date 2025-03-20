import config
import json
import re

from bs4 import BeautifulSoup
from loguru import logger
from datetime import datetime as dt

from pandas import read_excel
from docxtpl import DocxTemplate
from json import loads
from os import path, remove

def read_schedule():
    table = read_excel('./schedule.xlsx', header=None)
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
                if value == "9 - 21" and (current_hour > 6 + config.timezone and current_hour <= 18 + config.timezone):
                    current_user = table.iloc[i,0]
                    for j in range(2,8):
                        value = str(table.iloc[j, column])
                        if value == "21-9":
                            next_user = table.iloc[j,0]
                    return config.name_user[current_user], config.name_user[next_user]
                elif value == "9 - 21" and current_hour <= 6 + config.timezone:
                    next_user = table.iloc[i, 0]
                    for j in range(2,8):
                        value = str(table.iloc[j, column - 1])
                        if value == "21-9":
                            current_user = table.iloc[j, 0]
                    return config.name_user[current_user], config.name_user[next_user]
                elif value == "21-9" and current_hour > 18 + config.timezone:
                    current_user = table.iloc[i, 0]
                    for j in range(2,8):
                        value = str(table.iloc[j,column + 1])
                        if value == "9 - 21":
                            next_user = table.iloc[j,0]
                    return config.name_user[current_user], config.name_user[next_user]

#TODO: переписать/добавить функционал, чтобы не приходилось отсюда отправлять через объект бота
def make_docx_file(message, type_of_docs, bot) -> str:
    logger.info("Making docx file...")
    file_name_and_path = ''
    context = {}
    doc = None
    number = message.text
    name = config.user_fullname[config.tg_user['@' + message.from_user.username]]
    start_date = "" + str(dt.now().day) + "/" + str(dt.now().month) + "/" + str(dt.now().year) + " "
    end_date = start_date
    if type_of_docs == "3":
        doc = DocxTemplate("docx_template/database_check_template.docx")
        start_date += "15:00:00"
        end_date += "15:30:00"
        context = { 'number' : number, 'name' : name, 'start_date' : start_date, 'end_date' : end_date}
        file_name_and_path = f"documents/ЗНИ {number}. Отчёт о выполнении. БД.docx"
    elif type_of_docs == "2":
        doc = DocxTemplate("docx_template/reserve_copy_template.docx")
        start_date += "09:30:00"
        end_date += "10:00:00"
        context = { 'number' : number, 'name' : name, 'start_date' : start_date, 'end_date' : end_date}
        file_name_and_path = f"documents/ЗНИ {number}. Отчёт о выполнении. Резервные копии.docx"
    elif type_of_docs == "1":
        if dt.now().hour + config.timezone < 12:
            start_date += "07:00:00"
            end_date += "07:30:00"
        else:
            start_date += "19:00:00"
            end_date += "19:30:00"
        doc = DocxTemplate("docx_template/monitoring_check_template.docx")
        context = { 'number' : number, 'name' : name, 'start_date' : start_date, 'end_date' : end_date}
        file_name_and_path = f"documents/ЗНИ {number}. Отчёт о выполнении. Мониторинг.docx"
    doc.render(context)
    doc.save(file_name_and_path)
    logger.info(f"File \'{file_name_and_path}\' created and saved")
    file = open(file_name_and_path, "rb")
    bot.send_document(message.chat.id, file)
    logger.info(f"File sended to {message.from_user.username}")
    file.close()

def __json_comments_to_text(comments_json) -> str:
    text = []
    for comment in comments_json['comments']:
        for author in comments_json['comments'][comment]:
            text.append(f'''Автор: {author}\nСообщение: \n{comments_json['comments'][comment][author]}\n\n\n
                        ---------------------------------------------------------'''
                        .replace("<","").replace(">",""))
    return text

def comments_json_to_doc(json_path):
    logger.info("Starting creating docx from json")
    comments_json = {}
    try: 
        with open(json_path, 'r', encoding='utf-8') as file:
            comments_json = loads(file.read())
            logger.info("Json successfully readed")
    except Exception as e:
        logger.error(f"In creating docs file for comments get exception as {e}") #'messages' : comments_text,
        return

    ticket_id = comments_json['ticket_id']
    comments_text = __json_comments_to_text(comments_json)
    messages_count = len(comments_json['comments'])
    messages_template = ''
    docx = DocxTemplate("docx_template/comments_ticket_template.docx")
    for i in range(messages_count) : messages_template += "{{" + f" message{i} " + "}}\n"
    context = {'ticket_id' : ticket_id, 'messages' : messages_template, 'maked_date' : f"{dt.now().date()} {dt.now().time()}"}
    docx.render(context)
    docx.save(f"documents/{ticket_id}_comments_template.docx")
    logger.info("Template docx generated successfully")
    docx = DocxTemplate(f"documents/{ticket_id}_comments_template.docx")
    context = {}
    for i in range(messages_count):
        context.update({f'message{i}':comments_text[i]})
    docx.render(context)
    docx.save(f"documents/{ticket_id}_comments.docx")

    remove(f"documents/{ticket_id}_comments_template.docx")
    file = open(f"documents/{ticket_id}_comments.docx", 'rb')
    logger.info("Docx generated!")
    return file


def make_html_file(json_path):
    #тестовые авы
    image_support = "https://www.appengine.ai/uploads/images/profile/logo/NTechLab-AI.png"
    image_customer = "https://media.istockphoto.com/id/1332358775/photo/young-couple-shaking-hands-deal-contract-real-estate-investment-business-agreement-agent.jpg?s=612x612&w=0&k=20&c=tADtuQ9F_eKe_hMH0k5Ldg7N4p5BojisWf2n-jXar_I="
    result = ""

    with open(json_path, 'rb') as f:
        data = json.load(f)

    for item in data['comments']:
        user = next(iter(data['comments'][item].keys()))
        message = next(iter(data['comments'][item].values())).replace("\n", "<br>")
        code_blocks = re.findall(r'```(.*?)```', message, re.DOTALL)

        for code in code_blocks:
            message = message.replace(f'```{code}```', f'<pre class="code_block"><code>{code}</code></pre>')

        data['comments'][item][user] = message

        if user.endswith("ntechlab.com"): message = f'<div class="message sender"><p class="chatter"><img src="{image_support}">NtechLab Support Team | {user}</p><p><br>' + message + "</p></div>"
        else: message = f'<div class="message receiver"><p class="chatter"><img src="{image_customer}">Customer | {user}</p><p><br>' + message + "</p></div>"
        result += message

    soup =  BeautifulSoup(f'''<!DOCTYPE html>
    <html lang="ru">
     <head>
      <meta charset="utf-8"/>
      <meta content="width=device-width, initial-scale=1.0" name="viewport"/>
      <title>
       {data['ticket_id']}
      </title>
      <style>
       body {{
            background-color: #141414;
            color: #ffffff;
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 10px;
        }}        
        .chat-container {{
            max-width: 900px;
            margin: auto;
            padding: 10px;
            border: 2px solid #383838;
            border-radius: 7px;
            overflow-y: auto;
            height: 85vh;
        }}
        .message {{
            margin: 10px 0;
            padding: 10px;
            border-radius: 5px;
            position: relative;
        }}
        .message.sender {{
            background-color: #484949;
            align-self: flex-end;
        }}
        .message.receiver {{
            background-color: #ff3d3d73;
        }}
        .message p {{
            margin: 0;
        }}
        .code_block {{
            white-space: pre-wrap;
            background-color: #201f1f;
            padding: 4px;
            border: 20px;
            overflow: auto;
            font-family: monospace;
            max-height: 400px;
            color:#e0e0e0;
        }}
        .chatter {{
            font-size: 10px;
            font-weight: bold;
            outline: #141414;
            color: #5aa7ff;
            display: flex;
            align-items: center;
        }}
        .chatter img {{
            margin-right: 10px;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            object-fit: cover;
            overflow: hidden;
        }}
      </style>
     </head>
     <body>
        <div class="chat-container" id="chat">
            {result}
        </div>
     </body>
    </html>''', 'html.parser')

    try:
        with open(f"comments_files/{data['ticket_id']}.html", 'w', encoding="utf-8") as file:
            file.write(soup.prettify())
    except Exception as e:
        logger.error(e)
    return f"comments_files/{data['ticket_id']}.html"