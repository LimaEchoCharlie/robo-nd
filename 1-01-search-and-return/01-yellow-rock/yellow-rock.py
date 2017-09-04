import cv2
import numpy as np
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import glob

def mask_yellow(img):
    """
    Create an array that masks out everything except yellow pixels.
    If a pixel is yellow, the corresponding element in the array is set to 255.
    Otherwise, the element is set to 0
    :param img: image
    :return: mask array. Same size as img with a single channel
    """

    # define range of yellow color in HSV
    lower_hsv = np.array([20, 100, 100])
    upper_hsv = np.array([30, 255, 255])

    # Convert RGB to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

    # Threshold the HSV image to get only yellow colors
    return cv2.inRange(hsv, lower_hsv, upper_hsv)

if __name__ == "__main__":

    input_images = []
    mask_images = []

    # load all the jpegs in the calibration folder
    for path in glob.glob('./calibration_images/*.jpg'):
        input_images.append(mpimg.imread(path))

    # for each input image, create a yellow mask array
    for img in input_images:
        mask_images.append(mask_yellow(img))

    # create a single plot with all the images
    # first row = input, second row = mask
    fig = plt.figure(figsize=(12,3))
    nrows = 2
    ncols = len( input_images )
    plot_number = nrows * 100 + ncols * 10

    for i, img in enumerate(input_images, 1):
        plt.subplot( plot_number + i )
        plt.imshow( img )

    for i, img in enumerate(mask_images, len(input_images)+1):
        plt.subplot( plot_number + i )
        plt.imshow( img, cmap='Greys' )

    plt.show()
