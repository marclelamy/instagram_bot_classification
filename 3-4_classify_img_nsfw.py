import src.useful as su
import src.labelling as sl
from nsfw_detector import predict
import pandas as pd
import sqlite3 
from caffeine import on
import os
import numpy as np
from tqdm.contrib.concurrent import process_map
from datetime import datetime
import json 
from flatten_json import flatten
from tqdm import tqdm


print(f'\n\n\n{datetime.now()}\n\n\n')

# Creating SQL database to store all the data for the project
con = sqlite3.connect('data/main_database.sqlite')
model = predict.load_model('nsfw.299x299.h5')


def predict_store(path): 
    result = predict.classify(model, path)
    df = pd.DataFrame(result[path], index=[0])
    df['photo_name'] = path.replace('data/photos/all_photos/', '').replace('_user_photo.png', '')
    df['username'] = df['photo_name'].str.split('_').str[0]

    return df.to_sql('nsfw', con, if_exists='append', index=False)

def predict_user(username):
    try: 
        for x in ['_pp_user_photo'] + [f'{num}_user_photo' for num in range(12)]: 
            username_path = f'data/photos/all_photos/{username}_{x}.png'
            if os.path.isfile(username_path): 
                predict_store(username_path)
    except Exception as e: 
        print(e)


def load_paths():
    all_paths = su.list_files('data/photos/all_photos/')
    valid = ['_pp_user_photo'] + [f'_{num}_user_photo' for num in range(12)] 
    all_p = [path for path in all_paths if any(subpath in path for subpath in valid)]
    return all_p

########################################
# Here is for generating the photos
########################################







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












#############







def convert_json (username):
    # Open json 
    try:
        # json_file = open(f"data/users_json/{username}_user_profile_data.json")
        json_file = open(username)
        data = json.loads(json.load(json_file))["_node"]
    except json.decoder.JSONDecodeError:
        return


    # useles json keys
    ban = ['edge_felix_video_timeline', 'edge_owner_to_timeline_media', 'edge_saved_media', 
            'edge_media_collections', 'edge_related_profiles']

    # Defining basic keys. Those are name, follower count, bio, etc. Basic infos
    basic_keys = [key for key in data.keys() if key not in ban]

    basic_info = flatten({key:data[key] for key in basic_keys})
    df_current_user = pd.DataFrame([basic_info])
    # username = df_current_user.loc[0, "username"]

    # Getting the data for all posts that are contained in lists. 
    df_current_user["video_count"] = data['edge_felix_video_timeline']["count"]
    df_current_user["post_count"] = data['edge_owner_to_timeline_media']["count"]

    last_12_posts = dict()
    posts = data['edge_owner_to_timeline_media']["edges"]
    last_12_posts["username"] = data["username"]
    last_12_posts["video_views"] = [post["node"]["video_view_count"] if "video_view_count" in post["node"].keys() else np.nan for post in posts]
    last_12_posts["display_url"] = [post["node"]["display_url"] for post in posts]
    last_12_posts["thumbnail_src"] = [post["node"]["thumbnail_src"] for post in posts]
    last_12_posts["accessibility_caption"] = [post["node"]["accessibility_caption"] for post in posts]
    last_12_posts["is_video"] = [post["node"]["is_video"] for post in posts]
    last_12_posts["likes"] = [post["node"]["edge_liked_by"]["count"] for post in posts]
    last_12_posts["comments"] = [post["node"]["edge_media_to_comment"]["count"] for post in posts]
    last_12_posts["timestamp"] = [post["node"]["taken_at_timestamp"] for post in posts]
    df_last_12_posts = pd.DataFrame(last_12_posts)


    # Changing list type to str as sqlite3 doesn't accept this type
    list_features = ['bio_links', 'biography_with_entities_entities', 'edge_mutual_followed_by_edges', 'pronouns']
    for column in list_features: 
        if column in df_current_user.columns:
            df_current_user[column] = df_current_user[column].apply(lambda x:  "_LIST_SEPARATOR_".join(x))

    return df_current_user, df_last_12_posts



def do(values):
    username, paths = values
    paths = paths.split(',')

    df_u = pd.DataFrame()
    df_l = pd.DataFrame()
    for jsonfile in paths: 
        try:
            converted = convert_json(jsonfile) 
            if converted == None: 
                print('none')
                continue 
            df_current_user, df_current_last_12_posts = converted 
        except UnicodeDecodeError: # If an error happened while fetching the data, no file
            continue 

        # concat dfs 
        df_u = pd.concat([df_u, df_current_user], axis=0)
        df_l = pd.concat([df_l, df_current_last_12_posts], axis=0)
    
    if df_u.shape[0] > 0 and df_u.shape[1] > 0:
        df_u.drop_duplicates().to_csv(f'data/users_json/profile/{username}_profile_data_json.csv', index=False)
    if df_l.shape[0] > 0 and df_l.shape[1] > 0:
        df_l.drop_duplicates().to_csv(f'data/users_json/last12/{username}_last12_photos_json.csv', index=False)




if __name__ == '__main__':
    on(display=True)




    # done_usernames = sl.load_table('nsfw')['username'].unique()

    # # paths = load_paths()
    # username = sl.load_table('predictions').query('username not in @done_usernames').sort_values('entropy', ascending=False)['username']
    # chunksize = len(username) // (8 * 4)
    # process_map(predict_user, username, max_workers=8, chunksize=chunksize)


    # print(f'\n\n\n{datetime.now()}\n\n\n')












    # # Load the data and display only the one from a 
    # query = '''
    # select 
    #     distinct
    #     username
    # from clean_comments_users_last12
    # --where username not in (select username from photos where photo_type = 'summary')
    # '''

    # # query = '''
    # # select 
    # #     distinct 
    # #     username 
    # # from force_summary_generation
    # # '''

    # # query = '''
    # # select 
    # # distinct 
    # #     ccul.username 

    # # from clean_comments_users_last12 ccul
    # # left join labels l using(username)
    # # left join predictions p using(username)
    # # where 1=1
    # #     and l.label2 is null
    # #     and (l.labelling_technique is null or l.labelling_technique = 'manual_labelling')
    # # order by l.label desc, p.prediction desc'''

    # done_usernames = sl.list_files('data/photos/image_summary', common=False)
    # usernames = load_users_to_label()['username'].unique()
    # print(len(usernames))
    # # usernames = [username for username in tqdm(usernames) if username not in done_usernames]
    # print(len(usernames))



    # # print("\n", len(usernames["username"]), usernames.loc[0, "username"])
    # chunksize = len(usernames) // (8 * 4)
    # process_map(sl.generate_card, usernames, max_workers=8, chunksize=chunksize)






####################################
    df_username_mapping = pd.read_sql_query('select * from username_mapping', con)
    cooler_names = dict(df_username_mapping.values)
    all_files = list(su.list_files('/Users/marclamy', subdir=True))

    all_files_names = []
    for file in all_files:
        if '_user_profile_data.json' in file: 
            all_files_names.append(file)

    len(all_files_names)
    #### Creating df with all files
    df_files = pd.DataFrame(all_files_names, columns=['full_path'])
    df_files
    df_files['original_username'] = df_files['full_path'].apply(lambda x: x.split('/')[-1].replace('_user_profile_data.json', ''))
    df_files['username'] = df_files['original_username'].map(cooler_names)
    #### Subsetting df files to keep only the ones in df main
    usernames_in_main = sl.load_main()['username'].unique()
    print(len(usernames_in_main))
    df_files = df_files.query('username.isin(@usernames_in_main)')
    print(df_files.shape)
    df_files = df_files.groupby('original_username', as_index=False)['full_path'].apply(','.join).reset_index(drop=True)
    values = df_files.values

    # userss = []
    # for text in all_files_names: 
    #     # text = rmv_photo_type(text)
    #     text = text.split('/')[-1].replace('_user_profile_data.json', '')
    #     extensions = ['_0_user_photo.png', '_1_user_photo.png', '_2_user_photo.png', '_3_user_photo.png', '_4_user_photo.png', '_5_user_photo.png', '_6_user_photo.png', '_7_user_photo.png', '_8_user_photo.png', '_9_user_photo.png', '_10_user_photo.png', '_11_user_photo.png', '_pp_user_photo.png', '_website_photo']
    #     for extension in extensions:
    #         text = text.replace(extension, '')


    #     userss.append(text)


    print('starting', len(values))
    chunksize = len(values) // (8 * 4)
    # chunksize = 1
    process_map(do, values, max_workers=8, chunksize=chunksize)