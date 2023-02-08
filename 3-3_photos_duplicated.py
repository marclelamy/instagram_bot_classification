import src.image as si
import src.useful as su
import src.labelling as sl
import pandas as pd
import numpy as np
import sqlite3
from tqdm.contrib.concurrent import process_map
from tqdm import tqdm
import os

con = sqlite3.connect('data/main_database.sqlite')


import caffeine
caffeine.on(display=True)




def main(combo):
    try:
        photo_name, photo_dupe = combo
        # if len(photo_dupe) < 10:
        #     return 

        # Cut photo, get all cut paths
        dir_name = 'data/photos/photos_cut/' + photo_name.replace('.png', '')
        if os.path.isdir(dir_name):
            all_cut_paths = su.list_files(dir_name)
            print('list files', dir_name)
        else:
            print('cut photos', dir_name)
            all_cut_paths = si.cut_photo(photo_name)

        for photo_dupe in tqdm(photo_dupe):
            results = []
            cv2_photo_dupe = si.open_image(f'data/photos/all_photos/{photo_dupe}')
            thresholds = []
            for cut_path in all_cut_paths:
                cv2_cut = si.open_image(cut_path)
                threshold = 1
                try:
                    while si.image_in_other_image(cv2_cut, cv2_photo_dupe, threshold) == False:
                        threshold -= 0.001
                except Exception as e: 
                    print(e, photo_name, photo_dupe)
                    continue
                
                thresholds.append(threshold)
            results.append([photo_name, photo_dupe, min(thresholds), max(thresholds), round(np.mean(thresholds), 5)])
                
            pd.DataFrame(results, columns=['photo_name', 'photo_dupe', 'min_threshold', 'max_threshold', 'mean_threshold']).to_sql('photos_cuts_comparison', con, if_exists='append', index=False)
    except Exception as e: 
        print('\n'*10, e, photo_name, '\n'*10)


if __name__ == '__main__':
    # Load photo name and photo name dupe
    query = '''
    select 
        distinct 
        pd.photo_name
        , pd.photo_name_dupe 
        
    from photos_dupes pd 
    left join photos_cuts_comparison pcc on pd.photo_name = pcc.photo_name and pd.photo_name_dupe = pcc.photo_dupe
    where 1=1
        and pcc.photo_name is null
    order by group_id asc
    '''


    df = pd.read_sql_query(query, con)
    print(df.shape)
    # photos_combo = [list(x) for x in photos_combo]

    # df_photos_combo = pd.read_sql_query(query, con)
    # group_ids = df_photos_combo['group_id'].unique()
    photo_combo_dict = {}

    for photo_name in tqdm(df['photo_name'].unique()):
        photo_combo_dict[photo_name] = df.query('photo_name == @photo_name')['photo_name_dupe'].tolist()


    process_map(main, photo_combo_dict.items(), max_workers=4, chunksize=1)
    # process_map(main, photos_combo, max_workers=8, chunksize=1)
    # for x in tqdm(photos_combo):
    #     main(x)

