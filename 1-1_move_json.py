import os 
from caffeine import on
import pandas as pd
from tqdm.contrib.concurrent import process_map
from tqdm import tqdm 
import shutil

import src.labelling as sl
import src.useful as su
import sqlite3 
import json 
from flatten_json import flatten

con = sqlite3.connect('data/main_database.sqlite')






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
    # Load username mapping
    # df_username_mapping = pd.read_sql_query('select * from username_mapping', con)
    # cooler_names = dict(df_username_mapping.values)
    
    # # list all files with users_profile_data.json on my laptop
    # all_files = list(su.list_files('/Users/marclamy', subdir=True))
    # all_files_names = []
    # for file in all_files:
    #     if '_user_profile_data.json' in file: 
    #         all_files_names.append(file)
    # print(f'{len(all_files_names) = }')

    # # Creating df with all files, adding username and cooler name
    # df_files = pd.DataFrame(all_files_names, columns=['full_path'])
    # df_files['original_username'] = df_files['full_path'].apply(lambda x: x.split('/')[-1].replace('_user_profile_data.json', ''))
    # df_files['username'] = df_files['original_username'].map(cooler_names)
    # print(f'{df_files.shape = }')

    # # Listing all usernames and all their json 
    # usernames_in_main = sl.load_main()['username'].unique()
    # df_files = df_files.query('username.isin(@usernames_in_main)')
    # df_files = df_files.groupby('original_username', as_index=False)['full_path'].apply(','.join).reset_index(drop=True)
    # values = df_files.values

    # # convert all jsons
    # print('starting', len(values))
    # chunksize = len(values) // (8 * 4)
    # process_map(do, values, max_workers=8, chunksize=chunksize)



    # Concat all csv and store them back 
    all_profile_dfs = [pd.read_csv(file) for file in tqdm(su.list_files('data/users_json/profile'))]
    df_profiles = pd.concat(all_profile_dfs, axis=0)
    df_profiles.to_csv('data/users_json/profiles.csv', index=False)
    df_profiles.to_sql('profiles', con, if_exists='replace', index=False)

    all_last12_dfs = [pd.read_csv(file) for file in tqdm(su.list_files('data/users_json/last12'))]
    df_last12 = pd.concat(all_last12_dfs, axis=0)
    df_last12.to_csv('data/users_json/last12.csv', index=False)
    df_last12.to_sql('last12', con, if_exists='replace', index=False)
    os.system('say "done"')