import csv
import datetime
import numpy as np
import pandas as pd
import requests

needDay = input(print("За какой день требуется найти вакансии?:"))
nowMonth = datetime.datetime.now().month
nowYear = datetime.datetime.now().year

header_list = ['name', 'salary_from', 'salary_to', 'salary_currency', 'area_name', 'published_at']
header_csv = header_list
file = open('HHvacants.csv', 'w', newline='', encoding='utf_8_sig')
writer = csv.DictWriter(file,fieldnames=header_csv)
writer.writeheader()

per_page = 100
hour = '00'
min_sec = '00'
for part_day in range(4):
    date_from = "{0}-{1}-{2}T{3}:00:00".format(nowYear, nowMonth, needDay,hour)
    hour = (part_day + 1) * 6
    if hour < 10:
        hour = '0' + str(hour)
    elif hour == 24:
        hour = 23
        min_sec = 59
    date_to = "{0}-{1}-{2}T{3}:{4}:{4}".format(nowYear, nowMonth, needDay, hour,min_sec)
    for page in range(20):
        if page == 20:
            per_page = 99
        url_HH = "https://api.hh.ru/vacancies?specialization=1&per_page={0}&page={1}&date_from={2}&date_to={3}".format(per_page,page,date_from,date_to)
        res = requests.get(url_HH).json()
        for vac in res['items']:
            dict_temp = {}
            dict_temp['name'] = vac['name']
            try:
                dict_temp['salary_from'] = vac['salary']['from']
                dict_temp['salary_to'] = vac['salary']['to']
                dict_temp['salary_currency'] = vac['salary']['currency']
            except:
                dict_temp['salary_from'] = ""
                dict_temp['salary_to'] = ""
                dict_temp['salary_currency'] = ""
            dict_temp['area_name'] = vac['area']['name']
            dict_temp['published_at'] = vac['published_at']
            writer.writerow(dict_temp)
file.close()
