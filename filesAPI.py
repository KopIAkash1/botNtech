import config

from datetime import datetime as dt
from pandas import read_excel

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
                
if __name__ == "__main__":
    print(read_schedule())