import pandas as pd
import sqlite3
from tqdm import tqdm
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# create a database (database name is mimic3.db)
conn = sqlite3.connect('mimic3.db')
csv_list = [csv_file for csv_file in os.listdir('./mimic-iii-clinical-database-1.4/') if csv_file.endswith('.csv')]

# load all csvs in mimic-iii-clinical-database-1.4 folder and save them in a database
for csv_file in csv_list:
    print('Loading ' + csv_file)
    df = pd.read_csv('./mimic-iii-clinical-database-1.4/' + csv_file, chunksize=1000000, iterator=True, low_memory=False)
    for chunk in tqdm(df):
        chunk.to_sql(csv_file[:-4], conn, if_exists='append', index=False)

# close the connection
conn.close()