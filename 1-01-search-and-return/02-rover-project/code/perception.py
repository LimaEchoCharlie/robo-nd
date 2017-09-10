import numpy as np
import cv2
from debug import current_frame_fidelity


frame_fidelity = current_frame_fidelity()

# Identify pixels above the threshold
# Threshold of RGB > 160 does a nice job of identifying ground pixels only
def color_thresh(img, rgb_thresh=(160, 160, 160)):
    # Create an array of zeros same xy size as img, but single channel
    color_select = np.zeros_like(img[:,:,0])
    # Require that each pixel be above all three threshold values in RGB
    # above_thresh will now contain a boolean array with "True"
    # where threshold was met
    above_thresh = (img[:,:,0] > rgb_thresh[0]) \
                & (img[:,:,1] > rgb_thresh[1]) \
                & (img[:,:,2] > rgb_thresh[2])
    # Index the array of zeros with the boolean array and set to 1
    color_select[above_thresh] = 1
    # Return the binary image
    return color_select


def invert_thresh(threshold_img, mask):
    return (threshold_img -1 ) * -mask

def find_rocks(img):
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
    return cv2.inRange(hsv, lower_hsv, upper_hsv)/255


# Define a function to convert from image coords to rover coords
def rover_coords(binary_img):
    # Identify nonzero pixels
    ypos, xpos = binary_img.nonzero()
    # Calculate pixel positions with reference to the rover position being at the 
    # center bottom of the image.  
    x_pixel = -(ypos - binary_img.shape[0]).astype(np.float)
    y_pixel = -(xpos - binary_img.shape[1]/2 ).astype(np.float)
    return x_pixel, y_pixel


# Define a function to convert to radial coords in rover space
def to_polar_coords(x_pixel, y_pixel):
    # Convert (x_pixel, y_pixel) to (distance, angle) 
    # in polar coordinates in rover space
    # Calculate distance to each pixel
    dist = np.sqrt(x_pixel**2 + y_pixel**2)
    # Calculate angle away from vertical for each pixel
    angles = np.arctan2(y_pixel, x_pixel)
    return dist, angles

# Define a function to map rover space pixels to world space
def rotate_pix(xpix, ypix, yaw):
    # Convert yaw to radians
    yaw_rad = yaw * np.pi / 180
    xpix_rotated = (xpix * np.cos(yaw_rad)) - (ypix * np.sin(yaw_rad))
                            
    ypix_rotated = (xpix * np.sin(yaw_rad)) + (ypix * np.cos(yaw_rad))
    # Return the result  
    return xpix_rotated, ypix_rotated

def translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale): 
    # Apply a scaling and a translation
    xpix_translated = (xpix_rot / scale) + xpos
    ypix_translated = (ypix_rot / scale) + ypos
    # Return the result  
    return xpix_translated, ypix_translated


# Define a function to apply rotation and translation (and clipping)
# Once you define the two functions above this function should work
def pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale):
    # Apply rotation
    xpix_rot, ypix_rot = rotate_pix(xpix, ypix, yaw)
    # Apply translation
    xpix_tran, ypix_tran = translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale)
    # Perform rotation, translation and clipping all at once
    x_pix_world = np.clip(np.int_(xpix_tran), 0, world_size - 1)
    y_pix_world = np.clip(np.int_(ypix_tran), 0, world_size - 1)
    # Return the result
    return x_pix_world, y_pix_world

# wrapper around pix_to_world to simplify call
def rover_to_world(x_rover, y_rover, Rover, scale):
    return pix_to_world(x_rover, y_rover,
                        Rover.pos[0], Rover.pos[1],
                        Rover.yaw, Rover.worldmap.shape[0],
                        scale)

# Define a function to perform a perspective transform
def perspect_transform(img, src, dst):
           
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))# keep same size as input image
    
    return warped

# move angle to (-180,180]
def unwrap_angle(angle):
    if angle > 180:
        angle -= 360
    return angle

# only trust the perspective transformation when the pitch and roll are near zero
def perspective_is_reliable(Rover):
    abs_roll = abs(unwrap_angle(Rover.roll))
    abs_pitch = abs(unwrap_angle(Rover.pitch))
    return (abs_pitch < 1.0) & (abs_roll < 1.0)

# create an array that will mask out the portions of the image that furthest from the eye
# the eye is at (max_x/2, max_y) and the eye is pointing -y
# mask is applied independently in the x and y direction
def near_eye_mask(shape, dtype, width_factor=0.2, depth_factor=0.2):
    y_limit = int(shape[0] * depth_factor)
    x_limit = int(shape[1] * width_factor / 2)
    mask = np.ones(shape, dtype=dtype)
    mask[0:y_limit,:] = 0
    mask[:,0:x_limit] = 0
    mask[:,(shape[1]-x_limit):shape[1]] = 0
    return mask

# Apply the above functions in succession and update the Rover state accordingly
def perception_step(Rover):
    # Perform perception steps to update Rover()
    # NOTE: camera image is coming to you in Rover.img

    # 1) Define source and destination points for perspective transform
    dst_size = 5
    # Set a bottom offset to account for the fact that the bottom of the image
    # is not the position of the rover but a bit in front of it
    # this is just a rough guess, feel free to change it!
    bottom_offset = 6
    source = np.float32([[14, 140], [301, 140], [200, 96], [118, 96]])
    destination = np.float32([[Rover.img.shape[1] / 2 - dst_size, Rover.img.shape[0] - bottom_offset],
                              [Rover.img.shape[1] / 2 + dst_size, Rover.img.shape[0] - bottom_offset],
                              [Rover.img.shape[1] / 2 + dst_size, Rover.img.shape[0] - 2 * dst_size - bottom_offset],
                              [Rover.img.shape[1] / 2 - dst_size, Rover.img.shape[0] - 2 * dst_size - bottom_offset],
                              ])

    # 2) Apply perspective transform
    warped = perspect_transform(Rover.img, source, destination)

    # 3) Apply color threshold to identify navigable terrain/obstacles/rock samples
    navigable = color_thresh(warped)
    near_mask = near_eye_mask(navigable.shape, dtype=navigable.dtype, width_factor=0.4, depth_factor=0.3)
    near_navigable = cv2.bitwise_and( np.copy(navigable), near_mask)

    # Obstacles are simply navigable inverted
    mask = perspect_transform(np.ones_like(Rover.img[:,:,0]), source, destination)
    obstacle = invert_thresh(navigable, mask)

    # identify the rock
    rock_sample = find_rocks(warped)

    # 4) Update Rover.vision_image (this will be displayed on left side of screen)
    Rover.vision_image[:,:,0] = obstacle*255        # color-thresholded binary image
    Rover.vision_image[:,:,1] = rock_sample*255     # color-thresholded binary image
    Rover.vision_image[:,:,2] = navigable*180       # terrain color-thresholded binary image
    Rover.vision_image[:,:,2] = near_navigable*255  # terrain color-thresholded binary image


    # 5) Convert map image pixel values to rover-centric coords
    xpix_navigable, ypix_navigable = rover_coords(navigable)
    xpix_near_navigable, ypix_near_navigable = rover_coords(near_navigable)
    xpix_obstacles, ypix_obstacles = rover_coords(obstacle)
    xpix_rocks, ypix_rocks = rover_coords(rock_sample)

    # 6) Convert rover-centric pixel values to world coordinates
    scale = 2 * dst_size
    near_navigable_x_world, near_navigable_y_world = rover_to_world(xpix_near_navigable, ypix_near_navigable, Rover, scale)
    obstacle_x_world, obstacle_y_world = rover_to_world(xpix_obstacles, ypix_obstacles, Rover, scale)
    rock_x_world, rock_y_world = rover_to_world(xpix_rocks, ypix_rocks, Rover, scale)

    # 7) Update Rover worldmap (to be displayed on right side of screen)
    if perspective_is_reliable(Rover):
        Rover.worldmap[obstacle_y_world, obstacle_x_world, 0] = 255
        Rover.worldmap[near_navigable_y_world, near_navigable_x_world, 2] = 255

    Rover.worldmap[rock_y_world, rock_x_world, 1] = 255

    frame_fidelity.save_frame(Rover,(near_navigable_x_world, near_navigable_y_world))

    # 8) Convert rover-centric pixel positions to polar coordinates
    # Update Rover pixel distances and angles
    rover_centric_pixel_distances, rover_centric_angles = to_polar_coords(xpix_navigable, ypix_navigable)
    Rover.nav_dists = rover_centric_pixel_distances
    Rover.nav_angles = rover_centric_angles

    return Rover