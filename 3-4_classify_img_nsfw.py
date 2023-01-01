import src.useful as su
import src.labelling as sl
from nsfw_detector import predict
import pandas as pd
import sqlite3 
from caffeine import on
import os
from tqdm.contrib.concurrent import process_map


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
    for x in ['_pp_user_photo'] + [f'{num}_user_photo' for num in range(12)]: 
        username_path = f'data/photos/all_photos/{username}_{x}.png'
        if os.path.isfile(username_path): 
            predict_store(username_path)



def load_paths():
    all_paths = su.list_files('data/photos/all_photos/')
    valid = ['_pp_user_photo'] + [f'_{num}_user_photo' for num in range(12)] 
    all_p = [path for path in all_paths if any(subpath in path for subpath in valid)]
    return all_p

########################################
# Here is for generating the photos
########################################

if __name__ == '__main__':
    on(display=True)

    done_usernames = sl.load_table('nsfw')['username'].unique()

    # paths = load_paths()
    username = sl.load_table('predictions').query('username not in @done_usernames').sort_values('entropy', ascending=False)['username']
    chunksize = len(username) // (8 * 4)
    process_map(predict_user, username, max_workers=2, chunksize=chunksize)


