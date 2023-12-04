import sys
import argparse
import glob
import os
import numpy as np
from tqdm import tqdm 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from utiles_map import *

def map_creator(imgs_directory_path, save_path, num_neighbors, board_area_inches):
    '''
    This function creates an area map based on the input binary images that contains calibration boards with known area. 
    It processes each image to construct an area map which reflects the pixels area in inches square.
        Parameters:
            imgs_directory_path (str): Path to the directory containing binary images.
            save_path (str): Path where the constructed maps will be saved.
            num_neighbors (int): Number of neighbors to be consider for KNN-Regressor in order to fill the zeros within the area map.
            board_area_inches (float): The area of the calibration board in inches square.
    '''
    print('Starting Process.....')
    #get images paths
    masks_paths=glob.glob(os.path.join(imgs_directory_path,'*.png'))

    # Wrap the main loop with tqdm for the progress bar
    for i,img_path in enumerate(tqdm(masks_paths, desc='Processing Images')):
        #read image in binary format
        img=img_read_binary(img_path)
        #Initialize the area_map
        if i==0:
            #create an empty image of zeros
            area_map = np.zeros_like(img,dtype=np.float64)
        #check if the processed binary image does not contain any mask
        if np.sum(img)==0:
            continue
        #update the area map
        area_map= area_map_constructor(path=img_path,main_map=area_map,board_area_inch=board_area_inches)# Area of A4 board. 96.85

    area_map_saver(save_path,area_map,num_neighbors)
    saving_path=os.path.join(save_path,'results_area_map')
    print(f'End of Process! The constructed maps were saved in {saving_path}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='''Create an area map based on the input binary images that contains calibration boards.
                                      The map will reflect the area represented by each pixel in inches squared.''')
    parser.add_argument("imgs_directory_path", help="Path to the directory containing binary images.")
    parser.add_argument("save_path", help="Path where the constructed maps will be saved.")
    parser.add_argument("num_neighbors", type=int, help="Number of neighbors to be consider for KNN-Regressor in order to fill the zeros within the area map.")
    parser.add_argument("board_area_inches", type=float, help="The area of the calibration board in inches squared.")

    args = parser.parse_args()
    
    map_creator(args.imgs_directory_path, args.save_path, args.num_neighbors, args.board_area_inches)