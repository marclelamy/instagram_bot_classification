import src.labelling as sl

import pandas as pd 
import sqlite3  

import pygame 

import time
from datetime import datetime 
import os

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import *



# Connect to db and initialize pygame and load the main df with all users' data
con = sqlite3.connect('data/main_database.sqlite')
pygame.init()
query = '''
    select 
        distinct 
        * 
    from clean_comments_users_last12'''
df_main = pd.read_sql_query(query, con)

# Create the display surface object
display_surface = pygame.display.set_mode((1300, 450))
pygame.display.set_caption('Image')



def load_users_to_label():
    # List usernames to be proposed
    query = '''
            with all_labels as (
            select distinct * from labels
            union all 
            select distinct * from manual_labelling
            )
            select 
                p.username
                , p.legit_proba	
                , p.bot_proba
                , p.predicted_label
                , p.entropy
            from predictions p
            left join all_labels a using (username)
            where entropy > 0.2 or labelling_technique is null
            group by 1
            having group_concat(labelling_technique) = 'manual_labelling' or a.labelling_technique is null
            order by entropy desc
            '''
    query = f'''
    with all_labels as (
    select 
        distinct 
        username 
        , group_concat(labelling_technique)  as labelling_technique
        
    from (select distinct * from labels
            union all 
            select distinct * from manual_labelling) 
    group by 1
    )

    select 
        p.username
        , p.legit_proba	
        , p.bot_proba
        , p.predicted_label
        , p.entropy
    from predictions p
    left join all_labels a using(username)
    where labelling_technique = 'manual_labelling' or a.username is null
    group by 1,2,3,4,5
    order by entropy desc
    ''' 
    

    # showing users with russian characters first
    # chars = ['А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ж', 'З', 'И', 'Й', 'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т', 'У', 'Х', 'Ч', 'Ш', 'Ы', 'Ь', 'Э', 'Ю', 'Я']
    # usernames_russe = sl.load_main().query('comment.str.contains("|".join(@chars)) or biography.str.contains("|".join(@chars))')['username'].unique()

    # users with high porno or porno + sexy score (bots are mainly porn, )
    usernames_sexy = pd.read_sql_query('select username from nsfw group by 1 having avg(porn ) > .3', con)['username'].unique()

    df = pd.read_sql_query(query, con)
    # df = df.query('username in @usernames_russe').reset_index(drop=True)
    # df = df.query('username in @usernames_sexy').reset_index(drop=True)
    return df



def subset_user_data(username):
    # Create a subset of main 
    df_user = df_main[df_main['username']==username].reset_index(drop=True)
    return df_user



def load_labelled_users():
    # List usernames to be proposed
    query = '''
    select 
        distinct 
        * 
    from manual_labelling'''

    users_to_label = pd.read_sql_query(query, con)
    return users_to_label



def update_image(image_user_path):
    # Loading the image
    image = pygame.image.load(image_user_path)
    display_surface.blit(image, (0, 0))
    pygame.display.update() 



def which_key():
    '''Return which arrow key pressed'''

    key_direction = {pygame.K_LEFT: 'left',
                     pygame.K_RIGHT: 'right',
                     pygame.K_DOWN: 'down',
                     pygame.K_UP: 'up',
                     pygame.K_o: 'o'}

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                try:
                    return key_direction[event.key]
                except:
                    if pygame.key.name(event.key) == 'q':
                        pygame.quit()
                    print('WRONG KEY, PRESS AGAIN')
                    which_key()



def label_user(username, label):
    # Add result to a dataframe and export it
    # conn = sqlite3.connect('data/main_database.sqlite')
    dt = datetime.now()
    result = [username, label, dt, 'manual_labelling']
    df = pd.DataFrame([result], columns=['username', 'label', 'time', 'labelling_technique'])
    print(df)
    df.to_sql('manual_labelling', con, if_exists='append', index=False)
    return dt




def terminal_infos(df_current_user, color):
    '''Infos to print in the terminal for each user
    '''
    str_to_print = ''

    for comment in df_current_user['comment']:
        str_to_print += comment + '\n'

    str_to_print += '\n' * 5 + color

    print(str_to_print)



def update_label(label, dt):
    query = f'''
    UPDATE manual_labelling
    SET label = {label}
    WHERE time = "{dt}"'''

    con.execute(query)



def train_model():
    query = '''
    select 
        *
    from clean_comments_users_last12
    left join labels using(username)
    where label = label2'''

    df_ml = pd.read_sql_query(query, con)
    df_ml['label'] = df_ml['label'].str.replace('bot', '1').str.replace('legit', '0').astype(int)
    df_ml = df_ml.select_dtypes(include=['int', 'float']).dropna(axis=0)

    X = df_ml.drop('label', axis=1)
    y = df_ml['label']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)

    clf = RandomForestClassifier(max_depth=2, random_state=0)
    clf.fit(X_train, y_train)
    y_train_pred = clf.predict(X_train)
    y_pred_test = clf.predict(X_test)

    for function in (accuracy_score, recall_score, precision_score, matthews_corrcoef, auc):
        try:
            print(f'{function.__name__}: {function(y_train, y_train_pred).round(2)} | {function(y_test, y_pred_test).round(2)}')
        except:
            pass


def propose_user(username):
    df_current_user = subset_user_data(username)

    update_image(f'data/photos/image_summary/{username}_image_summary.png')



def prediction_color (next_prediction):
    if next_prediction >= .50: 
        return '🟥'*3000
    elif .50 > next_prediction >= .30: 
        return '🟧'*3000
    else:
        return '🟩'*3000



def main():
    df_users_to_label = load_users_to_label()
    print(f'{df_users_to_label.shape[0] = }')

    label_count = [0, 0]
    time_start = time.time()
    for index in range(df_users_to_label.shape[0]): 
        print(df_users_to_label.iloc[index-10:index+20].head(30))
        # If labelled 500 or spent 10 minutes, stop the program
        time_diff = int(time.time() - time_start)
        if sum(label_count) == 500 or time_diff > 600: 
            break

        # Loading user's data and checking if already labelled
        current_username, current_legit_proba, current_bot_proba, current_prediction, current_entropy = df_users_to_label.loc[index, :]
        df_current_user = subset_user_data(current_username)
        next_index = index
        if index < df_users_to_label.shape[0] - 2: 
            next_index += 1
        next_username, next_prediction, next_entropy = df_users_to_label.loc[next_index,['username', 'predicted_label', 'entropy']]
        df_next_user = subset_user_data(next_username)
            
        if index > 0: 
            past_username, past_prediction, past_entropy = df_users_to_label.loc[index-1,['username', 'predicted_label', 'entropy']]
            df_past_user = subset_user_data(past_username)


        # Print past rows labelled
        print(pd.read_sql_query('select * from manual_labelling', con).tail(5), '\n'*5)

        # Generate summary if the user doesn't have one
        image_user_path = f'data/photos/image_summary/{current_username}_image_summary.png'
        if os.path.exists(image_user_path) == False:
            # sl.generate_card(current_username)
            continue

 
        # Propose a user and print to the 
        try: 
            propose_user(current_username)
        except pygame.error:
            print(f'pygame.error: Error reading the PNG file for user', current_username)
            continue
        
        # Print major infos to terminal
        color = prediction_color(next_prediction)
        terminal_infos(df_current_user, color)
        print(sl.load_table('manual_labelling').query('username == @current_username'), '\n'*5)
        print(f'{current_username = }\n{current_prediction = }\n{next_prediction = }\n{current_entropy = }\n{current_legit_proba = }\n{current_bot_proba = }\n{label_count = }\n{sum(label_count) = }\n{time_diff = }')
        print(f'{df_users_to_label.shape[0] - index = }')

        # Capture which key pressed and export
        key_pressed = which_key()
        
        key_press_choices = {'right': 1, 'up': 0, 'down': 2, 'o': 3}
        if key_pressed == 'left':
            propose_user(past_username)
            key_pressed = which_key()
            update_label(key_press_choices[key_pressed], past_label_dt)

        
        elif key_pressed in key_press_choices.keys():
            past_label_dt = label_user(current_username, key_press_choices[key_pressed])
            if key_pressed == 'right': 
                label_count[0] += 1
            elif key_pressed == 'up': 
                label_count[0] += 1



if __name__ == '__main__':
    main()