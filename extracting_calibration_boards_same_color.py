import argparse
import glob
import os
import numpy as np
import cv2
from pathlib import Path

def extracting_calibration_boards_same_color(imgs_directory_path,save_path):
    '''
    This function was designed for processing a set of images to identify and extract regions corresponding to specific color ranges.
    It operates on a directory of .png images, applying color segmentation based on predefined color ranges.
    For each image, the function applies Gaussian blurring, converts the image to the HSV color space, and then creates masks for each color range.
    It calculates the area of the masked regions, filters out regions below a certain size threshold, and finds contours within these regions.
    Finally, it generates filled polygon masks for these contours and saves these masks as separate files.
        
    '''
    all_imgs_path=glob.glob(os.path.join(imgs_directory_path,'*.png'))

    for img_path in all_imgs_path:
        # Load your image (replace 'your_image.jpg' with your image file)
        image = cv2.imread(img_path)
        image = cv2.GaussianBlur(image, (7, 7), 0)

        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        for i,color_range in enumerate(colors.values()):
            # Create a mask for color range
            color_range_img = cv2.inRange(hsv_image,*color_range)
            #find coords of color:
            color_range_pix_coord=np.argwhere(color_range_img == 255)
            poly_area= mask_area(color_range_pix_coord)[0]
            #filter out empty images:
            if poly_area < 200:
                continue

            # Find contours
            contours, _ = cv2.findContours(color_range_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            approx_contours = [cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True) for cnt in contours]
            # Find the filled polygon using the fill_polygon function
            filled_polygon_mask = fill_polygon(approx_contours)

            
            save_filled_mask(filled_polygon_mask, file_path= os.path.join(save_path,Path(img_path).stem+f'_mask_{i}'+Path(img_path).suffix))
