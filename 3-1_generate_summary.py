import src.useful as su
import src.labelling as sl
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError
from caffeine import on


import pandas as pd 
import numpy as np
import sqlite3 
import plotly.io as pio

import os
import shutil

from tqdm.contrib.concurrent import process_map
from tqdm import tqdm

# Creating SQL database to store all the data for the project
database = "data/main_database.sqlite"
con = sqlite3.connect(database)




def load_users_to_label():
    # List usernames to be proposed
    query = '''
    with all_labels as (
    select * from labels 
    union all 
    select * from manual_labelling
    )

    select 
    distinct 
        ccul.username 
        , l.label
        , l.label2
        , round(p.prediction, 5) prediction


    from clean_comments_users_last12 ccul
    left join all_labels l using(username)
    left join predictions p using(username)
    where 1=1
        and l.label2 is null
        and (l.labelling_technique is null or l.labelling_technique = 'manual_labelling')
    order by l.label desc, p.prediction desc'''

    return pd.read_sql_query(query, con)



def load_users_to_label():
    # List usernames to be proposed
    query = '''
            with all_labels as (
            select distinct username, label, labelling_technique from labels
            union all 
            select distinct username, label, labelling_technique from manual_labelling
            )
            select 
                p.username
                , count(username) as count
                , group_concat(labelling_technique) as labelling_technique
                , p.entropy
            from predictions p
            left join all_labels a using (username)
            where entropy > 0.2 or labelling_technique is null
            group by 1
            having group_concat(labelling_technique) = 'manual_labelling' or a.labelling_technique is null
            order by entropy desc
            '''

    labelled_usernames = sl.load_labels()['username'].tolist()
    df = pd.read_sql_query(query, con).query('username not in @labelled_usernames').reset_index(drop=True)
    return df



# generate_card('nickliounis')

########################################
# Here is for generating the photos
########################################

if __name__ == '__main__':
    on(display=True)

    # Load the data and display only the one from a 
    query = '''
    select 
        distinct
        username
    from clean_comments_users_last12
    --where username not in (select username from photos where photo_type = 'summary')
    '''

    # query = '''
    # select 
    #     distinct 
    #     username 
    # from force_summary_generation
    # '''

    # query = '''
    # select 
    # distinct 
    #     ccul.username 

    # from clean_comments_users_last12 ccul
    # left join labels l using(username)
    # left join predictions p using(username)
    # where 1=1
    #     and l.label2 is null
    #     and (l.labelling_technique is null or l.labelling_technique = 'manual_labelling')
    # order by l.label desc, p.prediction desc'''

    done_usernames = sl.list_files('data/photos/image_summary', common=False)
    usernames = load_users_to_label()['username'].unique()
    print(len(usernames))
    # usernames = [username for username in tqdm(usernames) if username not in done_usernames]
    print(len(usernames))



    # print("\n", len(usernames["username"]), usernames.loc[0, "username"])
    chunksize = len(usernames) // (8 * 4)
    process_map(sl.generate_card, usernames, max_workers=8, chunksize=chunksize)


