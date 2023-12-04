import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from scipy.spatial import ConvexHull

def image_reader(img_path):
    '''This function takes a path of an image and then reads it and return an RGB image array.'''
    image = cv2.imread(img_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    img_dim=list(image.shape[:2])
    return image,img_dim


def find_mode_of_coordinates(coordinates):
    """
    Find the mode of a set of coordinates.

    :param coordinates: NumPy array of coordinates.
    :return: Mode of the coordinates.
    """
    mode_result = stats.mode(coordinates, axis=0,keepdims=True)
    mode_values = mode_result.mode
    return mode_values[0]


def mask_area(mask,img_width,img_height):
    '''
    This function computes the area of a mask within a binary image.
        Parameters:
            mask: Array representing a binary image.
            img_width: Image width, int.
            img_height: Image height,int.
        return:
            The area percent of the non zero bixels with respect to the binary image. 
    '''
    total_area=int(img_width*img_height)
    mask_area=np.count_nonzero(mask)
    mask_area_percent= (mask_area/ total_area)
    return mask_area,mask_area_percent


def polygon_coordinates(polygon):
    '''
    This function takes polygon vertices and processes and refines them to produce a closed polygon.
    Depending on the number of vertices, this function fits the convex hull algo to find the vertices
    of the polygon that have all of the points lying in it (Convexity).
        Parameters:
            polygon: Array containing the vertices of a polygon.
        return
            Array containing vertices of a refined polygon.
        '''    
    if polygon.shape[0]<3:
        
        # Draw the polygon
        polygon = plt.Polygon(polygon)

        #get_polygon_coordinates
        polygon=polygon.xy
        polygon=polygon.astype(np.int32)
        
        return polygon
    
    else:     
        # Compute the convex hull
        hull = ConvexHull(polygon)

        # Get the vertices of the convex hull
        hull_points = polygon[hull.vertices]

        # Draw the polygon
        polygon = plt.Polygon(hull_points)

        #get_polygon_coordinates
        polygon=polygon.xy
        polygon=polygon.astype(np.int32)

        return polygon
    
# Function to fill the polygon with the largest area used when the boards have different colors
def fill_polygon(contours,img_width,img_height):
    '''
    This function takes contours as input and then approximates polygon vertices from them.
    The function next measures the area of the polygon with the goal of obtaining the greatest 
    area that corresponds to the calibration board. Finally, a binary image of the polygon vertices
    corresponding to the biggest area will be drawn. 
    Note: Use this function when the calibration boards have different colors.
        Parameters:
            contours: Array containing the contours.
            img_width: Image width, int.
            img_height: Image height,int.
        return
            A binary image containing the calibration board.          
    '''
    max_area = 0
    max_contour = None
    for contour in contours:
        contour=contour.squeeze()
        contour= contour.reshape(-1,2) if contour.ndim ==1 else contour
        # Get precise polygon coordinates using polygon_coordinates
        precise_contour = polygon_coordinates(contour)
        area = cv2.contourArea(precise_contour)
        if area > max_area:
            max_area = area
            max_contour = precise_contour
    mask = np.zeros((int(img_width), int(img_height)), dtype=np.uint8)
    if max_contour is not None:
        cv2.drawContours(mask, [max_contour], -1, color=1, thickness=cv2.FILLED)
    return mask

# Function to fill the polygon with the largest area used when the boards have similar color
def fill_two_polygons(contours,img_width,img_height):
    '''
    This function takes contours as input and then approximates polygon vertices from them.
    The function next measures the area of the polygon with the goal of obtaining the greatest 
    area that corresponds to the calibration board. Finally, a binary image of the polygon vertices
    corresponding to the biggest area will be drawn. 
    Note: Use this function when the calibration boards have similar color.
        Parameters:
            contours: Array containing the contours.
            img_width: Image width, int.
            img_height: Image height,int.
        return
            Two binary image containing the calibration boards.          
    '''
    # Initialize variables to track the top two contours and their areas
    max_area = second_max_area = 0
    max_contour = second_max_contour = None

    for contour in contours:
        contour = contour.squeeze()
        contour = contour.reshape(-1, 2) if contour.ndim == 1 else contour
        precise_contour = polygon_coordinates(contour)
        area = cv2.contourArea(precise_contour)

        # Update the top two contours and their areas
        if area > max_area:
            second_max_area, second_max_contour = max_area, max_contour
            max_area, max_contour = area, precise_contour
        elif area > second_max_area:
            second_max_area, second_max_contour = area, precise_contour

    mask1 = np.zeros((int(img_width), int(img_height)), dtype=np.uint8)
    mask2 = np.zeros((int(img_width), int(img_height)), dtype=np.uint8)
    # Fill the largest contour
    if max_contour is not None:
        cv2.drawContours(mask1, [max_contour], -1, color=1, thickness=cv2.FILLED)

    # Fill the second largest contour
    if second_max_contour is not None:
        cv2.drawContours(mask2, [second_max_contour], -1, color=1, thickness=cv2.FILLED)

    return mask1, mask2

def save_filled_mask(mask, file_path):
    """
    Save the filled mask to a file.

    Parameters:
        mask: The binary mask image to save.
        file_path: The path to the file where the mask image will be saved.
    """
    # Ensure the mask is in the right type to be saved (optional)
    mask_to_save = (mask * 255).astype(np.uint8)
    # Save the mask image
    cv2.imwrite(file_path, mask_to_save)
    
def color_range_initiator():
    '''This function initiates a dict with the upper and lower bounds of the HSV color range for both green and red.'''
    #range for green
    lower_green = np.array([50, 40, 100])
    upper_green = np.array([80, 255, 255])
    # range for red
    lower_red = np.array([160, 80, 100])
    upper_red = np.array([179, 255, 255])

    colors={
            'green': [lower_green,upper_green],
            'red': [lower_red,upper_red]
            }
    return colors
