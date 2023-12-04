import argparse
import glob
import os
import numpy as np
import cv2
from pathlib import Path
from ..src.utiles import *

def extracting_calibration_boards_similar_color(imgs_directory_path,save_path):
    '''
    This function was designed for processing a set of images to identify and extract regions corresponding to specific color 
    ranges. It operates on a directory of .png images, applying color segmentation based on predefined color ranges.
    For each image, the function applies Gaussian blurring, converts the image to the HSV color space,
    and then creates masks for each color range. It calculates the area of the masked regions, filters
    out regions below a certain size threshold, and finds contours within these regions. Finally, it generates filled polygon
    masks for these contours and saves these masks as separate files.        
    '''
    #initiat color ranges
    colors= color_range_initiator()
    #get images paths
    all_imgs_path=glob.glob(os.path.join(imgs_directory_path,'*.png'))

    for img_path in all_imgs_path:

        # Load your image (replace 'your_image.jpg' with your image file)
        image = cv2.imread(img_path)
        image = cv2.GaussianBlur(image, (7, 7), 0)
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        # Create a mask for color range
        color_range_img = cv2.inRange(hsv_image,*colors['green'])

        # Find contours
        contours, _ = cv2.findContours(color_range_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        approx_contours = [cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True) for cnt in contours]

        # Find the polygons corresponding to the highest two areas using the fill_two_polygons function
        largest_two_polygons = fill_two_polygons(approx_contours,img_width=color_range_img.shape[0],img_height=color_range_img.shape[1])

        for i, poly in enumerate(largest_two_polygons):
            color_range_pix_coord=np.argwhere(poly == 1)
            poly_area= mask_area(color_range_pix_coord,img_width=color_range_img.shape[0],img_height=color_range_img.shape[1])[0]

            if poly_area < 200:
                continue
            else:
                save_filled_mask(poly, file_path= os.path.join(save_path,Path(img_path).stem+f'_mask_{i}'+Path(img_path).suffix))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process images to extract calibration boards that has different colors.")
    parser.add_argument("imgs_directory_path", help="Path to the directory containing images.")
    parser.add_argument("save_path", help="Path where the output masks will be saved.")

    args = parser.parse_args()
    
    extracting_calibration_boards_similar_color(args.imgs_directory_path, args.save_path)
