import cv2
import os
import numpy as np
from sklearn.neighbors import KNeighborsRegressor

def fill_zeros_with_nearest(img,num_neighbors=100):
    '''This function takes the area map and fill the pixels that have area equal to zero'''
    # Get the x, y coordinates of all non-zero pixels
    nonzero_y, nonzero_x = np.nonzero(img)
    # Stack them together for KDTree
    nonzero_coords = np.column_stack((nonzero_y, nonzero_x))
    # Get the x, y coordinates of all zero pixels
    zero_y, zero_x = np.nonzero(img == 0)
    zero_coords = np.column_stack((zero_y, zero_x))
    # If there are no zero-valued pixels, just return the original image
    if zero_coords.shape[0] == 0:
        return img
    # Get the values of non-zero pixels
    nonzero_values = img[nonzero_y, nonzero_x]
    # Fit KNeighborsRegressor on non-zero pixels
    knn = KNeighborsRegressor(n_neighbors=num_neighbors)
    knn.fit(nonzero_coords, nonzero_values)
    # Predict the values of zero pixels
    img[zero_y, zero_x] = knn.predict(zero_coords)

    return img

def img_read_binary(img_path):
    '''This function reads an image in binary format and returns it.'''
    img=cv2.imread(img_path,0)

    binary_image=np.where(img>0,1,0)
    return binary_image

def get_pixel_area(image,board_area_inch=96.85):#area in inchs of the board
    '''This function estimates pixels areas and return the estimated area as a float.'''
    #divide the board area over the number of pixels represinting the board:
    pixel_area= board_area_inch/ np.sum(image)
    return pixel_area

def img_indices(image):
    '''This function takes an image and return the non-zero indices.'''
    img_idx=np.array(np.nonzero(image)).T #get the indices of the non-zero pixels and return the array as a 2D array [[y,x]]
    return img_idx

def find_common_indices(img_1_idx,img_2_idx):
    '''This function takes the indices of the non-zero pixels in two images, and returns the commom, intersection, indices between the tow images.
        Parameters:
            img_1_idx:  2d array contains the indices of the non-zero pixels in an image.
            img_2_idx:  2d array contains the indices of the non-zero pixels in an image.
    '''
    # Create structured arrays
    array1_view = np.ascontiguousarray(img_1_idx).view(np.dtype((np.void, img_1_idx.dtype.itemsize * img_1_idx.shape[1])))
    array2_view = np.ascontiguousarray(img_2_idx).view(np.dtype((np.void, img_2_idx.dtype.itemsize * img_2_idx.shape[1])))

    # Use in1d to find common rows
    intersected = np.in1d(array1_view, array2_view)

    # Extract common rows
    common_rows = img_1_idx[intersected]

    return common_rows



def area_map_constructor(path,main_map,board_area_inch):
    '''This is the main function that will create the area map.'''
    img_scaled=img_read_binary(path)
    pixel_area=get_pixel_area(img_scaled,board_area_inch)
    img_scaled=img_scaled* pixel_area
    
    img_scaled_idx,main_map_idx= img_indices(img_scaled), img_indices(main_map)

    common_rows=find_common_indices(img_scaled_idx,main_map_idx)

    if common_rows.size:
        # Calculate the average values at the overlapping indices
        average_values = (main_map[common_rows[:,0], common_rows[:,1]] + img_scaled[common_rows[:,0], common_rows[:,1]]) / 2
        # Update the main image with the average values at the overlapping indices
        main_map[common_rows[:,0], common_rows[:,1]] = average_values
        img_scaled[common_rows[:,0], common_rows[:,1]]=0
        main_map+=img_scaled   
    else:
        main_map+=img_scaled

    return main_map

def area_map_saver(saving_path,area_map,num_neighbors=100):
    '''
    This function saves two versions of the area map: the original and one that has been processed using KNN-Regressor
    to fill gaps in the original area map; the user can work with/modify either of these maps.
    The original will be labeled as such, while the processed map will be labeled as filled map.
    '''
    saving_path=os.path.join(saving_path,'results_area_map')
    os.makedirs(saving_path) 
    orig_name= 'original_map.npy'
    filled_name= 'filled_map.npy'
    np.save(os.path.join(saving_path,orig_name), area_map)
    np.save(os.path.join(saving_path,filled_name), fill_zeros_with_nearest(area_map,num_neighbors))
