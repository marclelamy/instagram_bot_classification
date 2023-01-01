import os
from os import listdir
from os.path import isfile, join
import pandas as pd
import demoji
from tqdm import tqdm



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



def count_emoji(text):
    """
    Counts the number of emoji in a string.

    Parameters
    ----------
    text : string
        Text containing emoji(s)
    Sorted: Boolean
        If True returns a sorted dictionary 
    
    Returns
    -------
    dictionary:
        Dictionary with all distinct emojis for 
        values and their count in the string. 
    """   
    
    if type(text) != str:
        text = "".join(text)

    emoji_count = {i:text.count(i) for i in demoji.findall(text).keys()}

    return emoji_count