import pandas as pd
import numpy as np
import sqlite3
from pathlib import Path
#
# Path('my_data.db').touch()
#
conn = sqlite3.connect('my_data.db')
c = conn.cursor()
#
# df = pd.read_csv("current.csv")
# df.to_sql('current',conn, if_exists='append', index = False)


def get_curr(row,index):
    time = row['published_at'].split('T')[0]
    year = time.split('-')[0]
    month = time.split('-')[1]
    if month[0] == '0':
        month = month[1]
    d = '{0}-{1}'.format(year,month)
    try:
        c.execute("SELECT * FROM  current WHERE date=?", (d,))
        fa = list(c.fetchone())
        curr = fa[index]
        # curr = df_curr.loc[df_curr['date'] == "{0}-{1}".format(year,month)]
        answer = curr
        if answer == ' ':
            answer = np.nan
    except:
        answer = np.nan
    return float(answer)

df = pd.read_csv("vacancies_dif_currencies.csv", encoding='utf_8_sig')
df_cur = pd.read_csv("current.csv")
salary_column = []
headers = list(df_cur.columns)
for row in df.iterrows():
    if pd.isna(row[1]['salary_to']):
        row[1]['salary_to'] = 0
    elif pd.isna(row[1]['salary_from']):
        row[1]['salary_from'] = 0
    if pd.isna(row[1]['salary_currency']):
        salary_column.append(row[1]['salary_currency'])
    else:
        ind = headers.index(row[1]['salary_currency'])
        salary_column.append((row[1]['salary_to'] + row[1]['salary_from']) * get_curr(row[1],ind))


df = df.replace({'salary_from':salary_column})
df = df.drop(['salary_to','salary_currency'], axis=1)
df = df.rename(columns={'salary_from':'salary'})
df.head(100).to_sql('head100',conn, if_exists='append', index = False)