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
    select 
        distinct 
        username 
    from clean_comments_users_last12
    left join labels using(username)
    where 1=1
        and label2 is null 
    order by label desc'''

    users_to_label = pd.read_sql_query(query, con)['username']
    return list(users_to_label)



def subset_user_data(username):
    # Create a subset of main 
    df_user = df_main[df_main["username"]==username].reset_index(drop=True)
    return df_user



def load_labelled_users():
    # List usernames to be proposed
    query = '''
    select 
        distinct 
        * 
    from labels'''

    users_to_label = pd.read_sql_query(query, con)
    return users_to_label



def update_image(image_user_path):
    # Loading the image
    image = pygame.image.load(image_user_path)
    display_surface.blit(image, (0, 0))
    pygame.display.update() 



def which_key():
    '''Return which arrow key pressed'''

    key_direction = {pygame.K_LEFT: "left",
                     pygame.K_RIGHT: "right",
                     pygame.K_DOWN: "down",
                     pygame.K_UP: "up"}

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



def label_username(df_all_labels, username, label, first_label):
    # Add result to a dataframe and export it
    result = [username, label, datetime.now(), "manual_labelling"]
    print(df_all_labels)
    if username not in df_all_labels['username'].tolist():
        df_all_labels.loc[len(df_all_labels), ['username', 'label', 'time', 'labelling_technique']] = result
    else:
        df_all_labels.loc[df_all_labels['username']==username, ['username', 'label2', 'time2', 'labelling_technique']] = result
    print(df_all_labels)

    return df_all_labels




def terminal_infos(df_current_user):
    '''Infos to print in the terminal for each user
    '''
    str_to_print = ''

    for comment in df_current_user['comment']:
        str_to_print += comment + '\n'
    
    emoji_dict = df_current_user["emoji_dict"].values[0]
    for key, value in eval(emoji_dict).items():
        str_to_print += f"{key} {value} | "

    print(str_to_print)



def modify_label(username, label):
    '''Modify existing label'''
    df_all_labels = load_labelled_users()
    
    if pd.isna(df_all_labels.loc[df_all_labels['username'] == username, 'label2']): 
        col = ''
    else:
        col = '2'

    query = f'''
            update labels
            set
                label{col} = {label}
            where username == {username}
            '''

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


def main():
    users_to_label = load_users_to_label()
    df_all_labels = load_labelled_users()

    for index, username in enumerate(users_to_label):
        image_user_path = f"data/photos/image_summary/{username}_image_summary.png"
        if os.path.exists(image_user_path) == False:
            continue
        else:
            update_image(image_user_path)


        # Loading user's data and checking if already labelled
        df_current_user = subset_user_data(username)
        df_last_user = subset_user_data(users_to_label[index-1])
        df_next_user = subset_user_data(users_to_label[index+1])
        first_label = username not in df_all_labels['username']

        if index % 5 == 0: 
            train_model()
        terminal_infos(df_current_user)

        # Capture which key pressed and export
        key_pressed = which_key()
        
        key_press_choices = {"right": 'bot', "up": 'legit', "down": 'maybe'}
        if key_pressed == 'left':
            key_pressed = which_key()
            modify_label(username, key_press_choices[key_pressed]) 
        
        elif key_pressed in ('right', 'up', 'down'):
            df_all_labels = label_username(df_all_labels, username, key_press_choices[key_pressed], first_label)
            
        df_all_labels.to_sql('labels', con, if_exists='replace', index=False)

        print(df_all_labels, '\n'*5)



main()