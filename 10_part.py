import pandas as pd
import numpy as np
import sqlite3
from pathlib import Path

Path('my_data.db').touch()

conn = sqlite3.connect('my_data.db')
c = conn.cursor()

df = pd.read_csv("current.csv")
df.to_sql('current',conn, if_exists='append', index = False)