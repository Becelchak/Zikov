import csv
import math
import re
# import prettytable
import os
import datetime
import string

import numpy as np
import openpyxl as op
from jinja2 import Environment, FileSystemLoader
from openpyxl.styles import Border, Side, Font
from openpyxl.utils import get_column_letter
from matplotlib import pyplot as plt
import matplotlib
import jinja2
import pdfkit
import wkhtmltopdf

from xlsx2html import xlsx2html

vacant_dic = {"name": "Название", "description": "Описание", "key_skills": "Навыки", "experience_id": "Опыт работы",
              "premium": "Премиум-вакансия", "employer_name": "Компания", "salary": "Оклад",
              "area_name": "Название региона", "published_at": "Дата публикации вакансии"}
currency_to_rub = {
    "AZN": 35.68,
    "BYR": 23.91,
    "EUR": 59.90,
    "GEL": 21.74,
    "KGS": 0.76,
    "KZT": 0.13,
    "RUR": 1,
    "UAH": 1.64,
    "USD": 60.66,
    "UZS": 0.0055,
}
formaterr_dict = {"AZN": "Манаты", "BYR": "Белорусские рубли",
                  "EUR": "Евро", "GEL": "Грузинский лари",
                  "KGS": "Киргизский сом", "KZT": "Тенге",
                  "RUR": "Рубли", "UAH": "Гривны",
                  "USD": "Доллары", "UZS": "Узбекский сум",
                  "noExperience": "Нет опыта",
                  "between1And3": "От 1 года до 3 лет",
                  "between3And6": "От 3 до 6 лет",
                  "moreThan6": "Более 6 лет",
                  "": "Нет значения"}


class InputConect():
    dataSet = ""
    dict_inYear_noName = {}
    dict_inYear_noName_salary = {}

    dict_inYear_WithName = {}
    dict_inYear_WithName_salary = {}

    dict_inYear_City = {}
    dict_inYear_City_salary = {}
    temp_dict = {}
    temp_salary_dict = {}

    def __init__(self, data):
        self.dataSet = data

    def fill_title(self, filling_list, dic_naming, table):
        global vacant_dic
        for text_info in vacant_dic:
            filling_list.append(dic_naming[text_info])
        if len(table.field_names) == 0:
            table.field_names = filling_list

    # Добавление вакансий в таблицу
    def prepare_vacancies(self, dataSet, dic_naming, table):
        global full_table_skills
        title_list = ["№"]
        self.fill_title(title_list, dic_naming, table)
        table.max_width = 20
        count = 0
        for row in dataSet.vacancies_objects:
            formated_row = self.formatter(row)
            for i in range(len(formated_row)):
                if i == 2:
                    temp_skills = '\n'.join(formated_row[i])
                    # Сторонний сбор данных для сортировки навыков
                    if not full_table_skills.__contains__(formated_row[0]):
                        full_table_skills[formated_row[0]] = []
                    if not list(full_table_skills[formated_row[0]]).__contains__(formated_row[i]):
                        full_table_skills[formated_row[0]].append(formated_row[i])

                    if len(temp_skills) > 100:
                        temp = list(temp_skills)
                        temp[100] = "..."
                        formated_row[i] = "".join(temp[0:101])
                    else:
                        formated_row[i] = temp_skills
                elif len(formated_row[i]) > 100:
                    temp = list(formated_row[i])
                    temp[100] = "..."
                    formated_row[i] = "".join(temp[0:101])
            count += 1
            table.add_row([count, formated_row[0], formated_row[1], formated_row[2], formated_row[3],
                           formated_row[4], formated_row[5], formated_row[6], formated_row[7], formated_row[8]])

    # Форматирование зарплаты, времени и стажа
    def formatter(self, rows):
        global full_table_date
        global formaterr_dict
        result = []
        format_dic = {}
        salar_min = rows.salary.prepare_salary(str(int(float(rows.salary.salary_from))))
        salar_max = rows.salary.prepare_salary(str(int(float(rows.salary.salary_to))))
        if rows.salary.salary_gross == "Нет":
            rows.salary.salary_gross = "С вычетом налогов"
        elif rows.salary.salary_gross == "Да":
            rows.salary.salary_gross = "Без вычета налогов"
        salary_mean = "{0} - {1}".format(salar_min, str(salar_max))
        salary_answer = "{0} ({1}) ({2})".format(str(salary_mean), formaterr_dict[rows.salary.salary_currency],
                                                 rows.salary.salary_gross)
        # Перенос данных в правильную форму листа
        format_dic['name'] = rows.name
        format_dic['description'] = rows.description
        format_dic['key_skills'] = rows.key_skills
        format_dic['experience_id'] = formaterr_dict[rows.experience_id]
        format_dic['premium'] = rows.premium
        format_dic['employer_name'] = rows.employer_name
        format_dic['salary'] = salary_answer
        format_dic['area_name'] = rows.area_name

        pre_date = rows.published_at.split("T")[0].split("-")
        # Сторонний сбор данных для сортировки даты
        temp_date_time = rows.published_at.split("T")[1].split("+")[0]
        if not full_table_date.__contains__(format_dic["name"]):
            full_table_date[format_dic["name"]] = []
        if not list(full_table_date[format_dic["name"]]).__contains__(temp_date_time):
            full_table_date[format_dic["name"]].append((temp_date_time, format_dic["area_name"]))
        rows.published_at = "{0}.{1}.{2}".format(pre_date[2], pre_date[1], pre_date[0])
        format_dic['published_at'] = rows.published_at
        for item in format_dic:
            result.append(format_dic[item])
        return result

    # Правила сортировки по скиллам
    # Поиск полного списка навыков для каждой строчки
    def find_full_skills(self, x, full_skills):
        list_skills = full_skills[x[1]]
        redact_skills = x[3].replace(".", "")
        index = 0
        for i in range(len(list_skills)):
            str_skills = '\n'.join(list_skills[i])
            if str(str_skills).__contains__(redact_skills):
                index = i
                break
        return list_skills[index]

    # Правила сортировки по дате
    def get_date_sort(self, x, full_date):
        city = x.area_name
        time = x.published_at.split('-')
        mili_time = time[2].split('T')[1].split('+')[0].split(':')

        if not self.dict_inYear_WithName.__contains__(int(time[0])) and (x.name.__contains__(self.dataSet.job_name)
                                                                         or x.name.__contains__(
                    self.dataSet.job_name.lower())):
            self.dict_inYear_WithName[int(time[0])] = 1
            self.dict_inYear_WithName_salary[int(time[0])] = (float(x.salary.salary_from)
                                                              * currency_to_rub[x.salary.salary_currency]
                                                              + float(x.salary.salary_to)
                                                              * currency_to_rub[x.salary.salary_currency]) \
                                                             / 2
        elif x.name.__contains__(self.dataSet.job_name) or x.name.__contains__(self.dataSet.job_name.lower()):
            self.dict_inYear_WithName[int(time[0])] += 1
            self.dict_inYear_WithName_salary[int(time[0])] += (float(x.salary.salary_from)
                                                               * currency_to_rub[x.salary.salary_currency]
                                                               + float(x.salary.salary_to)
                                                               * currency_to_rub[x.salary.salary_currency]) \
                                                              / 2
        if not self.dict_inYear_noName.__contains__(int(time[0])):
            self.dict_inYear_noName[int(time[0])] = 1
            self.dict_inYear_noName_salary[int(time[0])] = (float(x.salary.salary_from)
                                                            * currency_to_rub[x.salary.salary_currency]
                                                            + float(x.salary.salary_to)
                                                            * currency_to_rub[x.salary.salary_currency]) \
                                                           / 2
        elif self.dict_inYear_noName.__contains__(int(time[0])):
            self.dict_inYear_noName[int(time[0])] += 1
            self.dict_inYear_noName_salary[int(time[0])] += (float(x.salary.salary_from)
                                                             * currency_to_rub[x.salary.salary_currency]
                                                             + float(x.salary.salary_to)
                                                             * currency_to_rub[x.salary.salary_currency]) \
                                                            / 2
        if not self.temp_dict.__contains__(city):
            self.temp_dict[city] = 1
            self.temp_salary_dict[city] = (float(x.salary.salary_from)
                                           * currency_to_rub[x.salary.salary_currency]
                                           + float(x.salary.salary_to)
                                           * currency_to_rub[x.salary.salary_currency]) \
                                          / 2
        elif self.temp_dict.__contains__(city):
            self.temp_dict[city] += 1
            self.temp_salary_dict[city] += (float(x.salary.salary_from)
                                            * currency_to_rub[x.salary.salary_currency]
                                            + float(x.salary.salary_to)
                                            * currency_to_rub[x.salary.salary_currency]) \
                                           / 2
        return datetime.datetime(day=int(time[2].split('T')[0]),
                                 month=int(time[1]),
                                 year=int(time[0]),
                                 hour=int(mili_time[0]),
                                 minute=int(mili_time[1]),
                                 second=int(mili_time[2]))

    # Правила сортировки по опыту работу
    def get_year_sort(self, x):
        split_list = x.split(" ")
        max_year = 0
        count_ind = 0
        for word in split_list:
            if word.isdigit():
                count_ind += 1
                max_year = max(max_year, int(word))
        if count_ind == 1:
            max_year += 1
        return max_year

    # Сортировка таблицы по любому из столбцов
    def get_sort_table(self, dataSet, table, full_skills_skills, full_skills_date):
        column_for_sort = dataSet.sort_parameter
        index_column = list(table.field_names).index(column_for_sort)
        reversesort = dataSet.IsReverseSort
        if column_for_sort == "Навыки":
            sort_key = lambda x: len(self.find_full_skills(x, full_skills_skills))
            return sorted(table.rows, key=sort_key, reverse=reversesort)
        elif column_for_sort == "Дата публикации вакансии":
            sort_key = lambda x: self.get_date_sort(x, full_skills_date)
            return sorted(table.rows, key=sort_key, reverse=reversesort)
        elif column_for_sort == "Оклад":
            salar = Salary()
            sort_key = lambda x: salar.salary_sorter(x[index_column])
            return sorted(table.rows, key=sort_key, reverse=reversesort)
        elif column_for_sort == "Опыт работы":
            sort_key = lambda x: self.get_year_sort(x[index_column])
            return sorted(table.rows, key=sort_key, reverse=reversesort)
        elif column_for_sort != "":
            sort_key = lambda x: x[index_column]
            return sorted(table.rows, key=sort_key, reverse=reversesort)

    def get_sort_dataSet(self, dataSet, full_skills_date):
        column_for_sort = dataSet.sort_parameter
        # index_column = list(dataSet.title_piece).index(column_for_sort)
        reversesort = dataSet.IsReverseSort
        sort_key = lambda x: self.get_date_sort(x, full_skills_date)
        return sorted(dataSet.vacancies_objects, key=sort_key, reverse=reversesort)
        # elif column_for_sort == "Оклад":
        #   sort_key = lambda x: x.salary.salary_sorter(x.salary)
        #  return sorted(dataSet.vacancies_objects, key=sort_key, reverse=reversesort)
        # elif column_for_sort != "":
        #   sort_key = lambda x: x[index_column]
        #  return sorted(dataSet.vacancies_objects, key=sort_key, reverse=reversesort)

    def sorted_for_graf(self):
        dataSet.sort_parameter = "Дата публикации вакансии"
        self.dataSet = self.get_sort_dataSet(self.dataSet, full_table_date)
        for key in self.dict_inYear_noName.keys():
            self.dict_inYear_noName_salary[key] = math.floor(
                int(self.dict_inYear_noName_salary[key]) / self.dict_inYear_noName[key])
            if len(self.dict_inYear_WithName) > 0:
                self.dict_inYear_WithName_salary[key] = math.floor(
                    int(self.dict_inYear_WithName_salary[key]) / self.dict_inYear_WithName[key])
            else:
                self.dict_inYear_WithName[key] = 0
                self.dict_inYear_WithName_salary[key] = 0
        bad_city_vac_count = 0
        for city in self.temp_dict.keys():
            if self.temp_dict[city] >= math.floor(len(dataSet.vacancies_objects) / 100):
                try:
                    self.dict_inYear_City[city] = round(int(self.temp_dict[city]) / len(dataSet.vacancies_objects), 4)
                    self.dict_inYear_City_salary[city] = math.floor(
                        int(self.temp_salary_dict[city]) / self.temp_dict[city])
                except:
                    f = 6
            else:
                bad_city_vac_count += int(self.temp_dict[city]) / len(dataSet.vacancies_objects)
        self.dict_inYear_City["Другие"] = bad_city_vac_count


class DataSet():
    file_name = ""
    job_name = ""

    vacancies_objects = []
    title_piece = ["№"] + list(vacant_dic.values())
    # result_read = []
    sort_parameter = ""
    IsReverseSort = 0
    filter_for_table = []
    vacant_piece = []

    message_error = ""

    filter_atr = ""
    sort_atr = ""
    revers_atr = ""

    TypeFinishResult = ""

    def __init__(self):
        self.file_name = input("Введите название файла: ")
        self.job_name = input("Введите название профессии: ")
        self.TypeFinishResult = input("Каким должен быть результат? Вакансии или Статистика?")
        self.check_atr()
        # self.result_read = self.csv_filter(self.file_name, self)
        self.vacancies_objects = self.csv_filter(self.file_name, self)
        if len(self.vacancies_objects) == 0:
            print("Нет данных")
            exit()

    # Фильтрация содержимых файла
    def csv_filter(self, file, data):
        list_naming = []
        temp_read = self.csv_reader(file, data)
        for data in temp_read[1]:
            temp_dict = {}
            for i, row in enumerate(data):
                data[i] = data[i].replace('\n', ']')
                temp = re.split(r'<.*?>', data[i])
                if temp[0] == "True" or temp[0] == "TRUE":
                    temp[0] = "Да"
                elif temp[0] == "False" or temp[0] == "FALSE":
                    temp[0] = "Нет"
                data[i] = re.sub(r'\s+', ' ', ''.join(temp)).strip()
                descript = data[i].split("]")
                if len(descript) == 1:
                    descript = "".join(descript)
                else:
                    descript = "]".join(descript)
                temp_dict[temp_read[0][i]] = descript
            list_naming.append(Vacancy(temp_dict))
        return list_naming

    # Чтение файла
    def csv_reader(self, file_name, data_self):
        title_row = []
        data_row = []
        if os.stat(file_name).st_size == 0:
            data_self.message_error = "Пустой файл"
            print(data_self.message_error)
            exit()
        with open(file_name, 'r', encoding='utf_8_sig') as f:
            reader = csv.reader(f)
            for index, row in enumerate(reader):
                if index == 0:
                    title_row = row
                    normal_length = len(row)
                else:
                    if '' not in row and normal_length == len(row):
                        data_row.append(row)
        return title_row, data_row

    # Проверка атрибутов на корректность
    def check_atr(self):
        global vacant_dic
        if len(self.filter_atr) != 0:
            if not self.filter_atr.__contains__(':'):
                self.message_error = "Формат ввода некорректен"
                print(self.message_error)
                exit()
            parameter = self.filter_atr.split(":")[0]
            parameter_list = self.filter_atr.split(":")[1].split(", ")
            parameter_list[0] = parameter_list[0].strip()
            if not (list(vacant_dic.values()).__contains__(parameter) or parameter == "Идентификатор валюты оклада"):
                self.message_error = "Параметр поиска некорректен"
                print(self.message_error)
                exit()
            self.filter_for_table = self.filter_atr.split(":")
        if not list(vacant_dic.values()).__contains__(self.sort_atr) and not self.sort_atr == "":
            self.message_error = "Параметр сортировки некорректен"
            print(self.message_error)
            exit()
        else:
            self.sort_parameter = (lambda arg: arg if list(vacant_dic.values()).__contains__(arg) else "")(
                self.sort_atr)
        if not ["Да", "Нет", ""].__contains__(self.revers_atr):
            self.message_error = "Порядок сортировки задан некорректно"
            print(self.message_error)
            exit()
        else:
            self.IsReverseSort = (lambda arg: arg == "Да")(self.revers_atr)


class Vacancy():
    name = ""
    description = ""
    key_skills = []
    experience_id = ""
    premium = ""
    employer_name = ""
    salary = ""
    area_name = ""
    published_at = ""

    def __init__(self, vacant):
        self.name = vacant["name"]
        gross = "None"
        try:
            self.description = vacant["description"]
            self.key_skills = vacant["key_skills"].split(']')
            self.experience_id = vacant["experience_id"]
            self.premium = vacant["premium"]
            self.employer_name = vacant["employer_name"]
            gross = vacant["salary_gross"]
        except:
            f = 5
        self.salary = Salary(vacant["salary_from"], vacant["salary_to"], gross,
                             vacant["salary_currency"])
        self.area_name = vacant["area_name"]
        self.published_at = vacant["published_at"]


class Salary():
    salary_from = ""
    salary_to = ""
    salary_gross = ""
    salary_currency = ""

    def __init__(self, *args):
        if len(args) > 0:
            self.salary_from = args[0]
            self.salary_to = args[1]
            if args[2] != "None":
                self.salary_gross = args[2]
            self.salary_currency = args[3]

    # Перевод зарплаты в нужный вид для форматирования
    def prepare_salary(self, string_salary):
        list_numb = []
        count = 0
        for char in reversed(string_salary):
            if count < 3:
                list_numb.append(char)
                count += 1
            else:
                list_numb.append(" ")
                list_numb.append(char)
                count = 0
        return "".join(list_numb.__reversed__())

    # Сортировка по окладу (среднему)
    def salary_sorter(self, x):
        currency = x.salary_currency
        salar_min = float(x.salary_from) * currency_to_rub[currency]
        salar_max = float(x.salary_to) * currency_to_rub[currency]
        return (salar_min + salar_max) / 2


class report():
    # Характеристики
    border = 0
    font = 0

    # Наполнение
    total_year = []
    mean_salary = {}
    mean_salary_job = {}
    count_vac = {}
    count_vac_job = {}

    mean_salary_city = {}
    count_vac_city = {}

    book = 0

    def __init__(self, font, border):
        self.font = font
        self.border = border

    def generate_excel(self, years, data, book, name_job):
        self.total_year = years
        self.mean_salary = data[0]
        self.mean_salary_job = data[1]
        self.count_vac = data[2]
        self.count_vac_job = data[3]
        self.mean_salary_city = data[4]
        self.count_vac_city = data[5]

        # 1
        ws = book.active
        ws.title = "Статистика по годам"
        book.create_sheet("Статистика по городам", 1)
        ws['A1'] = "Год"
        ws['A1'].font = self.font

        ws['B1'] = "Средняя зарплата"
        ws['B1'].font = self.font

        ws['C1'] = "Средняя зарплата - {0}".format(name_job)
        ws['C1'].font = self.font

        ws['D1'] = "Количество вакансий"
        ws['D1'].font = self.font

        ws['E1'] = "Количество вакансий - {0}".format(name_job)
        ws['E1'].font = self.font

        for i in range(len(years)):
            ws['A{0}'.format(i + 2)] = years[i]
            ws['B{0}'.format(i + 2)] = self.mean_salary[years[i]]
            ws['C{0}'.format(i + 2)] = self.mean_salary_job[years[i]]
            ws['D{0}'.format(i + 2)] = self.count_vac[years[i]]
            ws['E{0}'.format(i + 2)] = self.count_vac_job[years[i]]

        column_widths = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for row in ws.rows:
            for i, cell in enumerate(row):
                column_widths[i + 1] = max(len((str)(cell.value)) + 1, column_widths[i + 1])
                cell.border = self.border
        for i in range(len(column_widths)):
            ws.column_dimensions[get_column_letter(i + 1)].width = column_widths[i + 1]

        # 2
        ws = book["Статистика по городам"]
        ws['A1'] = "Город"
        ws['A1'].font = self.font

        ws['B1'] = "Уровень зарплат"
        ws['B1'].font = self.font

        ws['D1'] = "Город"
        ws['D1'].font = self.font

        ws['E1'] = "Доля вакансий".format(name_job)
        ws['E1'].font = self.font

        cityes_salar = list(self.mean_salary_city.keys())
        cityes_vac = list(self.count_vac_city.keys())
        for i in range(len(cityes_salar)):
            ws['A{0}'.format(i + 2)] = cityes_salar[i]
            ws['B{0}'.format(i + 2)] = self.mean_salary_city[cityes_salar[i]]
            ws['D{0}'.format(i + 2)] = cityes_vac[i]
            ws['E{0}'.format(i + 2)] = self.count_vac_city[cityes_vac[i]]
            ws['E{0}'.format(i + 2)].number_format = "0%"

        column_widths = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for row in ws.rows:
            for i, cell in enumerate(row):
                column_widths[i + 1] = max(len((str)(cell.value)) + 1, column_widths[i + 1])
                cell.border = self.border
        for i in range(len(column_widths)):
            ws.column_dimensions[get_column_letter(i + 1)].width = column_widths[i + 1]


dataSet = DataSet()

# table = prettytable.PrettyTable()
# table.hrules = prettytable.ALL
# table.align = 'l'
full_table_skills = {}
full_table_date = {}

# Динамика зарплат по годам
sorter_master = InputConect(dataSet)
sorter_master.sorted_for_graf()

sorter_master.dict_inYear_City_salary = dict(
    sorted(sorter_master.dict_inYear_City_salary.items(), key=lambda item: item[1], reverse=True))
sorter_master.dict_inYear_City = dict(
    sorted(sorter_master.dict_inYear_City.items(), key=lambda item: item[1], reverse=True))

sumInList = sorter_master.dict_inYear_City["Другие"] + sum(list(dict(list(sorter_master.dict_inYear_City.items())[10:]).values()))
sorter_master.dict_inYear_City["Другие"] = 0
sorter_master.dict_inYear_City = dict(
    sorted(sorter_master.dict_inYear_City.items(), key=lambda item: item[1], reverse=True))
sorter_master.dict_inYear_City = dict(list(sorter_master.dict_inYear_City.items())[:10])
sorter_master.dict_inYear_City_salary = dict(list(sorter_master.dict_inYear_City_salary.items())[:10])

print("Динамика уровня зарплат по годам: {0}".format(sorter_master.dict_inYear_noName_salary))
print("Динамика количества вакансий по годам: {0}".format(sorter_master.dict_inYear_noName))
print("Динамика уровня зарплат по годам для выбранной профессии: {0}".format(sorter_master.dict_inYear_WithName_salary))
print("Динамика количества вакансий по годам для выбранной профессии: {0}".format(sorter_master.dict_inYear_WithName))
print("Уровень зарплат по городам (в порядке убывания): {0}".format(sorter_master.dict_inYear_City_salary))
print("Доля вакансий по городам (в порядке убывания): {0}".format(sorter_master.dict_inYear_City))

font_title = Font(name='Calibri',
                  size=11,
                  bold=True,
                  italic=False,
                  vertAlign=None,
                  underline='none',
                  strike=False,
                  color='FF000000')
border = Border(left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin'))

wb = op.Workbook()
if DataSet.TypeFinishResult == "Вакансии":
    #Таблица
    rep = report(font_title,border)
    data_for_excel = [sorter_master.dict_inYear_noName_salary,
               sorter_master.dict_inYear_WithName_salary,
                sorter_master.dict_inYear_noName,
                sorter_master.dict_inYear_WithName,
                sorter_master.dict_inYear_City_salary,
                sorter_master.dict_inYear_City]
    rep.generate_excel(list(sorter_master.dict_inYear_noName_salary.keys()),data_for_excel,wb,dataSet.job_name)
    wb.save("report.xlsx")
elif DataSet.TypeFinishResult == "Статистика":
    #Графики
    labels_years = list(sorter_master.dict_inYear_noName_salary.keys())
    salary_noName = list(sorter_master.dict_inYear_noName_salary.values())
    salart_Name = list(sorter_master.dict_inYear_WithName_salary.values())

    vac_noName = list(sorter_master.dict_inYear_noName.values())
    vac_Name = list(sorter_master.dict_inYear_WithName.values())

    cityes_salary = list(sorter_master.dict_inYear_City_salary.values())
    labels_cityes = list(sorter_master.dict_inYear_City.keys())

    sorter_master.dict_inYear_City["Другие"] = sumInList
    sorter_master.dict_inYear_City = dict(
        sorted(sorter_master.dict_inYear_City.items(), key=lambda item: item[1], reverse=True))
    circle_labels = list(sorter_master.dict_inYear_City.keys())
    cityes_perc = list(sorter_master.dict_inYear_City.values())

    width = 0.4
    x = np.arange(len(labels_years))
    y = np.arange(len(labels_cityes))

    matplotlib.rc('axes', titlesize=8)
    matplotlib.rc('font', size=8)
    matplotlib.rc('xtick', labelsize=8)
    matplotlib.rc('ytick', labelsize=8)
    matplotlib.rc('legend', fontsize=8)

    fig, ax = plt.subplots(2, 2)

    rects1 = ax[0, 0].bar(x - width / 2, salary_noName, width, label="Средняя з/п")
    rects2 = ax[0, 0].bar(x + width / 2, salart_Name, width, label="з/п {0}".format(dataSet.job_name))
    ax[0, 0].set_title('Уровень зарплат по годам')
    ax[0, 0].set_xticks(x)
    ax[0, 0].set_xticklabels(labels_years, rotation=90)
    ax[0, 0].legend()

    rects3 = ax[0, 1].bar(x - width / 2, vac_noName, width, label="Количество вакансий")
    rects4 = ax[0, 1].bar(x + width / 2, vac_Name, width, label="Количество вакансий {0}".format(dataSet.job_name))
    ax[0, 1].set_title('Количество вакансий по годам')
    ax[0, 1].set_xticks(x)
    ax[0, 1].set_xticklabels(labels_years, rotation=90)
    ax[0, 1].legend()

    rects5 = ax[1, 0].barh(y, cityes_salary, width * 2, align='center')
    ax[1, 0].set_title('Уровень зарплат по городам')
    ax[1, 0].set_yticks(y, labels=labels_cityes)
    ax[1, 0].set_yticklabels(labels_cityes, fontsize=6,
                             fontdict={'horizontalalignment': 'right', 'verticalalignment': 'center'})
    ax[1, 0].invert_yaxis()

    circle = ax[1, 1].pie(cityes_perc, labels=circle_labels, textprops={'fontsize': 6})
    ax[1, 1].set_title('Доля вакансий по городам', fontsize=6)
    ax[1, 1].axis('equal')

    plt.tight_layout()
    plt.show()
    fig.savefig("graph.png")

# В HTML

# ФИГНЯ ВАРИАНТ
#html_table_file = open("table_html",'w')
#
#xlsx2html("report.xlsx", "table_html", sheet=1)
#
#out_stream = xlsx2html('report.xlsx')
#out_stream.seek(0)
#result_html = out_stream.read()
#
#html_table_file.write(result_html)
#html_table_file.close()

# В PDF

#env = Environment(loader=FileSystemLoader('.'))
#template = env.get_template("shablon.html")

job_name = dataSet.job_name
path = "graph.png"

#env = Environment(loader=FileSystemLoader('.'))
#template = env.get_template("Shablon.html")



#pdf_template = template.render({'job_name' : job_name, 'excel': wb["Статистика по годам"]})
#config = pdfkit.configuration(wkhtmltopdf=r'E:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe')
#pdfkit.from_string(pdf_template, 'report.pdf', configuration=config)



#for row in wb["Статистика по годам"].rows:
#    for cell in row:
#{{Name_data}}
#{{title_data}}
#{% for data in enumerate(dataStrings) %}
#    {{data[0]}} | {{data[1]}} | {{data[2]}} | {{data[3]}} | {{data[4]}} |
#{% endfor %}

#{ %for row in excel.rows: %}
#{{row[0]}} < br >
#{ % endfor %}