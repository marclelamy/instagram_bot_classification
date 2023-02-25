import shutil 
import os
import pandas as pd
from tqdm import tqdm
import sqlite3
from tqdm.contrib.concurrent import process_map

database = "/Users/marclamy/Desktop/code/Instagram_bot_classification/data/main_database.sqlite"
con = sqlite3.connect(database)


usernames = pd.read_sql_query('select distinct * from comments', con).query('follow_count.isna()')['username'].str[:-8].unique()



file_list = []
for root, dirs, files in tqdm(os.walk('/Users/marclamy/Desktop')):
    for file in files:
        if 'json' in file:
            if 'Instagram_bot_classification/data/users_json' in file:
                continue

            file_list.append(root + '/' + file)




print('done')
real = []

# for file in tqdm(file_list):
def check(file):
    for username in usernames: 
        if username in file:
            name = file.split('/')[-1]
            shutil.copy(file, f'/Users/marclamy/Desktop/code/Instagram_bot_classification/data/new_json_from_null_follow_count/{name}')
            continue

for file in tqdm(file_list):
    check(file)
# if __name__ == '__main__':
#     chunksize = len(usernames) // (8 * 4)
#     process_map(file, file_list, max_workers=8, chunksize=chunksize)