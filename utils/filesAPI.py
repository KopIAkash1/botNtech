import config
import telebot

from loguru import logger
from datetime import datetime as dt
from pandas import read_excel
from docxtpl import DocxTemplate


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