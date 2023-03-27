import pandas as pd
import sqlite3
from tqdm import tqdm
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))


# create a database (database name is mimic3.db)
conn = sqlite3.connect('mimic4.db')
csv_list = [csv_file for csv_file in os.listdir('C:/Data/MIMIC4/mimic-iv-2.2_unzip/') if csv_file.endswith('.csv')]

# load all csvs in mimic-iii-clinical-database-1.4 folder and save them in a database

csv_list = os.listdir()
for csv_file in csv_list:
    print('Loading'+csv_file)
    df1 = pd.read_csv('C:/Data/MIMIC4/mimic-iv-2.2_unzip//hosp/'+ csv_file, chunksize=1000000, iterator=True, low_memory=False)
    df2 = pd.read_csv('C:/Data/MIMIC4/mimic-iv-2.2_unzip//icu/'+ csv_file, chunksize=1000000, iterator=True, low_memory=False )
    for chunk in tqdm(df1):
        chunk.to_sql(csv_file[:-4], conn, if_exists='append',index=False)
    for chunk in tqdm(df2):
        chunk.to_sql(csv_file[:-4], conn, if_exists='append',index=False)

# close the connection
conn.close()