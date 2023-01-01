import requests 
from bs4 import BeautifulSoup as bs
from splinter import Browser
from tqdm import tqdm 




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