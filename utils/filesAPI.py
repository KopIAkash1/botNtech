import config

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
