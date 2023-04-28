import requests 
from bs4 import BeautifulSoup as bs
from splinter import Browser
from tqdm import tqdm 
import json 
from flatten_json import flatten
import pandas as pd


def bsoup(url):
    """If url is type string, return a soup, beautiful soup object of the link, 
    otherwise of the browser. It would take a browser in the case where we're using
    Splinter and not Beautiful Soup """
    if type(url) == str: 

        resp = requests.get(url)
        return bs(resp.content, 'html.parser')
    else: 
        return bs(url.html, 'html.parser')


def tag_string(tag, html_element):
    """Returns the element of an html"""
    typ = html_element.split("=")[0]
    name = html_element.split("=")[1]
    return tag + f"[{typ}=" + "\"" + name + "\"]"


def launch_driver(path="chromedriver"):
    """Function that creates an instance of a Chrome page. It returns browser, an object of Splinter, itself using Selenium."""
    path = {"executable_path": path}

    # Starting driver. Headless displays the browser. 
    browser = Browser("chrome", **path, headless=False) 
    
    return browser



def convert_json (username):
    # Open json 
    try:
        json_file = open(f"data/users_json/{username}_user_profile_data.json")
        # json_file = open(username)
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