from IPython.display import Image as IImage, display, clear_output
import pandas as pd 
import plotly.express as px
import numpy as np
from datetime import datetime
import sqlite3 
import shutil 
import os 
from PIL import Image
# import useful as su
import os
from os import listdir
from os.path import isfile, join

# Connect to database 
con = sqlite3.connect('data/main_database.sqlite')

from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError







# load_labels(), show_label_count()
def load_labels(include_all=False, group_bots=False):
    '''Load usernames and their labels. 
    
    parameters
    include_all: if true, returns the union all of labels and manual_labelling table 
    group_bots: if true, otherbot, type 3 become type 1 else only legit users and bots are returned'''
    if include_all == True: 
        return pd.read_sql_query('''
                                 select distinct * from manual_labelling
                                 union all 
                                 select distinct * from labels
                                 ''',
                                 con)

    query = f'''
    with all_labels as (
    select 
        distinct 
        username 
        , label 
        , avg(label) over(partition by username) as avg_label
        , case 
            when group_concat(labelling_technique) over(partition by username) like "%miss_labelled_corrected%" and labelling_technique = "miss_labelled_corrected" then 1
            when group_concat(labelling_technique) over(partition by username) not like "%miss_labelled_corrected%" then 1
            else 0 
            end as row_to_keep --if username has a miss label corrected and another labelling technique, then the correction is the best in quality. If username have not mlc then we still want it
        , group_concat(labelling_technique) over(partition by username) as labelling_technique
        
    from (select distinct * from labels
          union all 
          select distinct * from manual_labelling) 
    )

    select
        username
        , case 
            when {group_bots} and label = 3 then 1
            else label 
            end as label
        , labelling_technique

    from all_labels
    where 1=1
        and labelling_technique != 'fakelabelling' 
        and row_to_keep == 1
        and label in (0, 1, 3)
        and label = avg_label
        and labelling_technique != "manual_labelling" --If a user has only one labelling technique and it's manual, the user hasn't been checked a second time

    --group by username 

    '''

    return pd.read_sql_query(query, con)

def load_table(table, where='1=1', select='distinct *'):
    query = f'''
    select 
        {select}
        
    from {table}
    where {where}'''
    return pd.read_sql_query(query, con)

def load_main():
    query = '''
    select 
        distinct
        *
        
    from clean_all_data
    where 1=1 
        and follow_count is not null'''
    return pd.read_sql_query(query, con)



class Mypandas(pd.DataFrame):
    @classmethod
    def initialize(self): 
        pd.DataFrame.better_value_count = self.better_value_count
        pd.DataFrame.column_user_distribution = self.column_user_distribution
        pd.DataFrame.split_df_by_colcat = self.split_df_by_colcat
        pd.DataFrame.describe_column_by_colcat = self.describe_column_by_colcat
        pd.DataFrame.outliers_bound = self.outliers_bound
        pd.DataFrame.find_outliers = self.find_outliers


    def better_value_count(self, column, round=3, dropna=True): 
        '''Returns a Dataframe with value count and value count
        normalized for a specific column.
        
        Parameter 
        ---------
        column, str: columns to get the value count from
        '''
        
        val_count = self[column].value_counts()
        val_count_normalized = self[column].value_counts(normalize=True).round(round)
        
        if dropna == False:
            val_count_na = self[column].value_counts(dropna=False)
            val_count_na_normalized = self[column].value_counts(dropna=False, normalize=True).round(round)

            df_val_count = pd.concat([val_count, val_count_normalized, val_count_na, val_count_na_normalized], axis=1)
            df_val_count.columns = ['wo_na', 'wo_na_norm', 'w_na', 'w_na_norm']

        else: 
            df_val_count = pd.concat([val_count, val_count_normalized], axis=1)
            df_val_count.columns = ['wo_na', 'wo_na_norm']

        return df_val_count.sort_values('wo_na_norm', ascending=False)


    def column_user_distribution (self, column_to_analyse, rmv_values=[], rmv_labelled_values=True):
        # Load and split data
        df_labels = load_labels(include_all=True)
        bots = df_labels.query('label == 1')['username'].tolist()
        otherbots = df_labels.query('label == 3')['username'].tolist()
        legits = df_labels.query('label == 0')['username'].tolist()
        df_main = self.query(f'{column_to_analyse} not in @rmv_values').reset_index(drop=True)

        df_main[column_to_analyse] = df_main[column_to_analyse].astype('category')
        df_bots = df_main.query("username in @bots")
        df_otherbots = df_main.query("username in @otherbots")
        df_legits = df_main.query("username in @legits")

        # Counting how many times each categories has been used 
        df_col = df_main[column_to_analyse].value_counts().to_frame().reset_index()
        df_col.columns = [column_to_analyse, "count"]

        for index, sub_df in enumerate([df_main, df_bots, df_legits, df_otherbots]):
            # Looking at how many distinct users used the categories and how many time the coment has been collected
            for num in [0, 3, 1]:
                sub_df = sub_df[["username", column_to_analyse]]
                column_name = ["user_count", "bot_count", "legit_count", 'otherbot_count'][index]

                # Removing duplicates and changing col name
                if num == 1: 
                    sub_df = sub_df.drop_duplicates()
                    column_name = column_name + "_unique" # for "no duplicate"


                # group by categories, get the count of username for each
                # comment_count = sub_df.groupby(column_to_analyse)\
                #                                 .count()\
                #                                 .reset_index()\
                #                                 .to_numpy()
                comment_count = sub_df[column_to_analyse].value_counts().reset_index().to_numpy()

                comment_count_dict = {i:j for i, j in comment_count}


                # Counting by how many users each categoriess has been used for
                df_col[column_name] = df_col[column_to_analyse].apply(lambda x: comment_count_dict[x] if x in comment_count_dict.keys() else 0)


        # Removing values that have been 100% labelled
        if rmv_labelled_values == True:
            df_col = df_col.query("count > bot_count + legit_count + otherbot_count")


        return df_col.sort_values(by="count", ascending=False).reset_index(drop=True)


    def split_df_by_colcat(self, col, itself=False): 
        '''Subset a df info multiple each having one label. 
        It returns n dfs, n being number of labels'''
        dfs = [self.query(f'{col} == {category}') for category in sorted(self[col].unique())]
        if itself == True:
            dfs = [self] + dfs
        return dfs


    def describe_column_by_colcat(self, column, colcat='label'): 
        '''Describes a given column for each value of another column'''
        all_dfs = []
        for df in self.split_df_by_colcat(colcat, itself=True): 
            outlier_bound = self.outliers_bound(column, df)
            df = df[column].describe()
            df['lower outlier'] = outlier_bound[0]
            df['upper outlier'] = outlier_bound[1]
            all_dfs.append(df)

        df_describe = pd.concat(all_dfs, axis=1).astype(int)#.iloc[1:] # Removing count column, redundant
        df_describe.columns = ['all'] + sorted(self.label.astype(int).unique())
        
        df_plolty = df_describe.stack().to_frame().reset_index()
        df_plolty.columns = ['Statistic', 'Label', 'value']
        fig = px.histogram(df_plolty,
                           x='Statistic',
                           y='value',
                           color='Label',
                           barmode='group',
                           title=f"Summary stats per label for column {column.replace('_', ' ')}"
                           ).update_layout(yaxis_title=column.replace('_', ' ').title())

        return df_describe, fig


    def outliers_bound(self, col, df=None):
        '''Given a column, return the lower and upper bounds for outliers'''
        if df is None:
            df = self

        q1, q3 = df[col].quantile([.25, .75])
        iqr = q3 - q1
        lower_bound = q1 - (1.5 * iqr)
        upper_bound = q3 + (1.5 * iqr)
        
        lower_bound = df[col].min() if lower_bound < df[col].min() else lower_bound
        upper_bound = df[col].max() if upper_bound > df[col].max() else upper_bound
        return lower_bound, upper_bound


    def find_outliers(self, col, bounds=[]):
        '''Given a columns, return a pd.Series with True/False for each value'''
        if len(bounds) == 2: 
            lower_bound, upper_bound = bounds
        else: 
            lower_bound, upper_bound = self.outliers_bound(col)

        return self[col].fillna(self[col].quantile(.5)).apply(lambda x: not lower_bound <= x <= upper_bound)



def show_label_count(returnit=False):
    df_labels = load_labels()
    df_main = load_main()
    df_labels = df_main.merge(df_labels, how='left', on='username').query('follow_count.notna() and label in (0, 1)')
    df_labels = Mypandas(df_labels)
    
    if returnit == True: 
        return df_labels.better_value_count('label')['wo_na'].sort_index()
    else : 
        display(df_labels.better_value_count('label'))







def list_files(directory, extension=True, path=True, replace=None, subdir=False, common=True):
    """Given a directory, return all the files is that directory. 
    Parameters: 
        - extensions: default True. If False, returns files names without the path before. Ex /user/Desktop/main.py --> main.py
        - path: default True. If False,returns the file names without the entension. Ex: /user/Desktop/main
        
        - If both False return name without path or extension."""

    if "/" != directory[-1]: directory = directory + "/"

    if subdir == False: 
        all_files_names = [os.path.join(directory, file) for file in listdir(directory) if isfile(join(directory, file)) and file != ".DS_Store"]

    else:
        all_files_names = []
        for (dirpath, dirnames, filenames) in os.walk(directory):
            all_files_names += [(dirpath + '/' + file ).replace('//', '/') for file in filenames]

    if extension == False:
        all_files_names = [[file[:len(file)-file[::-1].index(".")-1]][0] for file in all_files_names]

    if path == False:
        all_files_names = [directory + file  for file in all_files_names]

    if replace != None:
        all_files_names = [file.replace(replace, "") for file in all_files_names]
    
    if common in (False, 'dict'): 
        pre_common = os.path.commonprefix(all_files_names)
        post_common = os.path.commonprefix([x[::-1] for x in all_files_names])[::-1]
        all_files_names = [file.replace(pre_common, "").replace(post_common, "") for file in all_files_names]
    
    return all_files_names



# show_user_summary() - Creating a function that I can call whevener I want to see a user's summary. this helps a lot when having to decide on a user class
def show_user_summary(usernames):
    # Making sure username is a list
    if type(usernames) == str:
        usernames = [usernames]
    else:
        usernames = list(usernames)
    usernames = list(set(usernames))

    # removing all files from folder
    if os.path.isdir('data/photos/temprary_user_summary/'):
        for file in list_files('data/photos/temprary_user_summary/', path=True):
            os.remove(file)

    # displaying or storing the photos depending on the number ( above 50 is too big for notebook which might crash or become slow)
    if len(usernames) > 50: 
        show = False 
        print("Greater than 50")
    else: 
        show = True

    for username in usernames:
        source_path = f"data/photos/image_summary/{username}_image_summary.png"
        look_up_path = f"data/photos/temprary_user_summary/{username}_image_summary.png"
        try:
            if show == True:
                display(Image.open(source_path))
            else: 
                shutil.copy(source_path, look_up_path)
        except FileNotFoundError:
            print(f"File not found for {username}")

    print(os.getcwd() + '/data/photos/temprary_user_summary/')





# label_users() - label users in df_main
# def label_users (new_users: list, label: str, labelling_type: str):
#     before_count = show_label_count(returnit=True)
    
#     # Creating df and exporting it
#     df_labels = pd.read_sql_query('select distinct * from labels', con)
#     already_labelled = df_labels['username'].tolist()
#     dtypes = {'username': 'object', 'label': 'Int64', 'time': '<M8[ns]', 'label2': 'Int64', 'time2': '<M8[ns]', 'labelling_technique': 'object'}
#     all_data = [[username, label, datetime.now(), np.nan, np.nan, labelling_type] for username in new_users]
#     df_new_labels = pd.DataFrame(all_data, columns=['username', 'label', 'time', 'label2', 'time2', 'labelling_technique'])

#     df_labels = pd.concat([df_new_labels, df_labels], axis=0).drop_duplicates()
#     df_labels = df_labels.astype(dtypes)
#     df_labels.to_sql('labels', con, if_exists='replace', index=False)

    
#     print(f'Usernames already in: {len([x for x in new_users if x in already_labelled])}\nNew usernames: {len([x for x in new_users if x not in already_labelled])}\n')

#     after_count = show_label_count(returnit=True)
#     # print(after_count)
#     count_diff = {int(i):after_count[int(i)] - before_count[int(i)] for i in after_count.index}
#     print('New labels:')
#     for key, value in count_diff.items():
#         print(f"{key}: {value}")

#     return show_label_count()



def label_users(new_usernames: list, label: int, labelling_type: str):
    dt = datetime.now()
    data = [[username, label, dt,labelling_type] for username in new_usernames]
    df = pd.DataFrame(
                data=data, 
                columns=['username', 'label', 'time', 'labelling_technique']
                )
    df.to_sql('labels', con, if_exists='append', index=False)

# def label_users (new_usernames: list, label: int, labelling_type: str):
#     df_main = pd.read_sql_query('select username from clean_comments_users_last12', con)
#     before_count = df_main.merge(load_labels(), how='left', on='username')['label'].value_counts()

#     # Loading labels and creating new labels df
#     # df_labels = pd.read_sql_query('select distinct username from labels', con)
#     # already_labelled_username = df_labels['username'].tolist()
#     # dtypes = {'username': 'object', 'label': 'Int64', 'time': '<M8[ns]', 'label2': 'Int64', 'time2': '<M8[ns]', 'labelling_technique': 'object'}

#     # Filtering out already labelled usernames and exporting the data by appending it to existing label table
#     new_labels_data = [[username, label, datetime.now(), np.nan, np.nan, labelling_type] for username in new_usernames]
#     df_new_labels = pd.DataFrame(new_labels_data, columns=['username', 'label', 'time', 'label2', 'time2', 'labelling_technique'])
#     df_new_labels.to_sql('labels', con, if_exists='append', index=False)


#     after_count = df_main.merge(load_labels(), how='left', on='username')['label'].value_counts()
#     count_diff = {int(i):after_count[int(i)] - before_count[int(i)] for i in after_count.index}
#     print('New labels:')
#     for key, value in count_diff.items():
#         print(f"{key}: {value}")



def clean_post_posted_time(x):
    x = x.split(',')
    return (pd.to_datetime(x[0]) - pd.to_datetime(x[-1])).days
# Load the data and display only the one from a 
query = '''
select 
    * 
from clean_comments_users_last12
'''
df_main = pd.read_sql_query(query, con)
# df_main['posts_days_diff'] = df_main['posts_posted_time'].apply(lambda x: clean_post_posted_time(x) if x != None else x)




def generate_card(username):
    df_user = df_main[df_main["username"]==username].reset_index(drop=True)
    # print('\n', df_user, '\n', username, '\n'*10)

    # Create new image
    global_image = Image.new("RGB", (1300, 450), "black")
    draw = ImageDraw.Draw(global_image)
    font = ImageFont.truetype("assets/OpenSans-Light.ttf", 15)

    # Open user pp and add it to the global image
    try:
        path = f"data/photos/user_profile_pictures/{username}_pp_user_photo.png"
        profile_pic = Image.open(path)
        global_image.paste(profile_pic, (250, 0))
    except (FileNotFoundError, UnidentifiedImageError): 
        pass

    # Creating a list of position to add the photos on the global image
    positions = []
    for x in range(850, 1300, 150):
        for y in range(0, 450, 150):
            positions.append((x, y))


    # Loop trhough each image and add it to the global image
    # user_last12_path = f"data/7_user_last_12_csv/{username}_last12.csv"
    # if os.path.exists(user_last12_path):
    #     last_12 = pd.read_csv(user_last12_path)
    for image_num in range(12):
        path = f"data/photos/user_last_12_posts/{username}_{str(image_num)}_user_photo.png"
        
        try:
            if os.path.exists(path):
                img = Image.open(path)
                if image_num < 9:
                    global_image.paste(img.resize((150, 150)), positions[image_num])
                elif image_num == 9:
                    global_image.paste(img.resize((150, 150)), (400, 0))
                elif image_num == 10:   
                    global_image.paste(img.resize((150, 150)), (550, 0))
                elif image_num == 11:
                    global_image.paste(img.resize((150, 150)), (700, 0))
        except (OSError, UnidentifiedImageError) as e: # For truncated image file
            print("OSError/PIL: ", e)



    # Add basic information 
    username = df_user.loc[0, "username"]
    draw.text((10, 5), f"Username: {username}", font=font, fill="white")

    follower_count = df_user.loc[0, "follower_count"]
    color = "white" if follower_count > 800 else "red"
    draw.text((10, 25), f"Followers: {follower_count:,}", font=font, fill=color)

    follow_count = df_user.loc[0, "follow_count"]
    draw.text((10, 45), f"Following: {follow_count:,}", font=font, fill="white")

    post_count = df_user.loc[0, "post_count"]
    color = "white" if post_count > 16 else "red"
    draw.text((10, 65), f"Post count: {post_count}", font=font, fill=color)

    video_count = df_user.loc[0, "video_count"]
    color = "white" if video_count > 0 else "red"
    draw.text((10, 85), f"Video count: {video_count}", font=font, fill=color)

    comments_likes = round(df_user["comments_likes"].mean())
    color = "white" if 200 <= comments_likes < 450 else "red"
    draw.text((10, 105), f"Comments_likes: {comments_likes}", font=font, fill="white")

    domain = df_user.loc[0, "domain"]
    draw.text((10, 125), f"{domain}", font=font, fill="white")

    biography = df_user.loc[0, "biography"]
    draw.text((10, 145), f"{biography}", font=font, fill="white")

    comment = '\n'.join(df_user["comment"])
    line_breaks = biography.count('\n') if biography != None else 0
    draw.text((10, 165 + line_breaks * 20), f"{comment}", font=font, fill="red")

    posts_days_diff = df_user.loc[0, "posts_days_diff"]
    color = "white" if posts_days_diff > 0 else "red"
    draw.text((10, 305), f"{posts_days_diff = }", font=font, fill=color)
    
    time_difference = '-'.join(df_user["time_difference"].astype(str))
    color = "white" if df_user["time_difference"].mean() > 90 else "red"
    draw.text((10, 325), f"{time_difference = }", font=font, fill=color)


    # Save screenshot, open it, resize it, add it to global_image and deleting the file
    path = f"data/photos/bio_url_screenshot/{username}_website_photo.png"
    try:
        screenshot = Image.open(path)
        global_image.paste(screenshot.resize((500, 300)), (350, 150))
    except (UnidentifiedImageError, FileNotFoundError):
        pass


    # Export image
    summary_path = f"data/photos/image_summary/{username}_image_summary.png"
    global_image.save(summary_path)
    pd.DataFrame({'username': [username], 
                  'photo_type': ['summary'], 
                  'path': [path]}).to_sql('photos', con, if_exists='append', index=False)