import src.useful as su
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError
from caffeine import on


import pandas as pd 
import numpy as np
import sqlite3 
import plotly.io as pio

import os
import shutil

from tqdm.contrib.concurrent import process_map 

pd.set_option("display.max_columns", None)
pio.templates.default = "plotly_dark"

# Creating SQL database to store all the data for the project
database = "data/main_database.sqlite"
con = sqlite3.connect(database)




# Load the data and display only the one from a 
query = '''
select 
    * 
from clean_comments_users_last12
'''
df_main = pd.read_sql_query(query, con)

def generate_card(username):
    df_user = df_main[df_main["username"]==username].reset_index(drop=True)

    # Create new image
    global_image = Image.new("RGB", (1300, 450), "white")
    draw = ImageDraw.Draw(global_image)
    font = ImageFont.truetype("OpenSans-Light.ttf", 15)

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
    draw.text((10, 5), f"Username: {username}", font=font, fill="black")

    follower_count = df_user.loc[0, "follower_count"]
    color = "black" if follower_count > 800 else "red"
    draw.text((10, 25), f"Followers: {follower_count:,}", font=font, fill=color)

    follow_count = df_user.loc[0, "follow_count"]
    draw.text((10, 45), f"Following: {follow_count:,}", font=font, fill="black")

    post_count = df_user.loc[0, "post_count"]
    color = "black" if post_count > 16 else "red"
    draw.text((10, 65), f"Post count: {post_count}", font=font, fill=color)

    video_count = df_user.loc[0, "video_count"]
    color = "black" if video_count > 0 else "red"
    draw.text((10, 85), f"Video count: {video_count}", font=font, fill=color)

    comment_likes = round(df_user["comment_likes"].mean())
    color = "black" if 200 <= comment_likes < 450 else "red"
    draw.text((10, 105), f"Comment_likes: {comment_likes}", font=font, fill="black")

    domain = df_user.loc[0, "domain"]
    draw.text((10, 125), f"{domain}", font=font, fill="black")

    biography = df_user.loc[0, "biography"]
    draw.text((10, 145), f"{biography}", font=font, fill="black")

    comment = '\n'.join(df_user["comment"])
    draw.text((10, 145), f"{comment}", font=font, fill="black")


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
    where username not in (select username from photos where photo_type = 'summary')
    '''
    usernames = pd.read_sql_query(query, con)



    print("\n", len(usernames["username"]), usernames.loc[0, "username"])

    process_map(generate_card, usernames["username"], max_workers=8, chunksize=1)

