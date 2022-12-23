from PIL import Image 
from itertools import product
import os 
import cv2 
import numpy as np




def cut_photo(photo_name):
    name = photo_name.replace('.png', '')
    photo_path = 'data/photos/all_photos/' + photo_name

    img = Image.open(photo_path)
    w, h = img.size
    d = w//3
    
    # Create directory if doesnt exists
    directory = os.getcwd() + f'/data/photos/photos_cut/{name}/'
    if os.path.isdir(directory) == False: 
        os.mkdir(directory)

    all_cuts_paths = []
    grid = product(range(0, h-h%d, d), range(0, w-w%d, d))
    for i, j in grid:
        box = (j, i, j+d, i+d)
        # out = os.path.join(dir_out, f'{name}_{i}_{j}{ext}')
        out = directory + f'{name}_{i}_{j}.png'
        img.crop(box).save(out)
        all_cuts_paths.append(out)

    return all_cuts_paths


def open_image(paths):
    if type(paths) == str: 
        img = cv2.imread(paths)
    else:
        img = [cv2.imread(path) for path in paths]
    
    return img



def image_in_other_image(cut: np.ndarray, image: np.ndarray, threshold=.95, save_image=False):
    # Compare image
    res = cv2.matchTemplate(cut, image, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)

    # Places a rectangle on the image where the cut is and save it
    if save_image == True:
        w, h = image.shape[:-1]
        for pt in zip(*loc[::-1]):  # Switch collumns and rows
            cv2.rectangle(cut, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)

        cv2.imwrite(f'/Users/marclamy/Desktop/shit delete anytime/ase/{np.random.randint(1000000)}.png', image)  

    return len(list(zip(*loc[::-1]))) > 0