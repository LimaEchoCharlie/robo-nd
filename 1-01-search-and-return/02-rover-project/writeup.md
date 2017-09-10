## Project: Search and Sample Return
### Writeup Template: You can use this file as a template for your writeup if you want to submit it as a markdown file, but feel free to use some other method and submit a pdf if you prefer.

---


**The goals / steps of this project are the following:**  

**Training / Calibration**  

* Download the simulator and take data in "Training Mode"
* Test out the functions in the Jupyter Notebook provided
* Add functions to detect obstacles and samples of interest (golden rocks)
* Fill in the `process_image()` function with the appropriate image processing steps (perspective transform, color threshold etc.) to get from raw images to a map.  The `output_image` you create in this step should demonstrate that your mapping pipeline works.
* Use `moviepy` to process the images in your saved dataset with the `process_image()` function.  Include the video you produce as part of your submission.

**Autonomous Navigation / Mapping**

* Fill in the `perception_step()` function within the `perception.py` script with the appropriate image processing functions to create a map and update `Rover()` data (similar to what you did with `process_image()` in the notebook). 
* Fill in the `decision_step()` function within the `decision.py` script with conditional statements that take into consideration the outputs of the `perception_step()` in deciding how to issue throttle, brake and steering commands. 
* Iterate on your perception and decision function until your rover does a reasonable (need to define metric) job of navigating and mapping.  

[//]: # (Image References)

[image1]: ./misc/rover_image.jpg
[image2]: ./calibration_images/example_grid1.jpg
[image3]: ./calibration_images/example_rock1.jpg 

## [Rubric](https://review.udacity.com/#!/rubrics/916/view) Points
### Here I will consider the rubric points individually and describe how I addressed each point in my implementation.  

---
### Writeup / README

#### 1. Provide a Writeup / README that includes all the rubric points and how you addressed each one.  You can submit your writeup as markdown or pdf.  

You're reading it!

### Notebook Analysis
#### 1. Run the functions provided in the notebook on test images (first with the test data provided, next on data you have recorded). Add/modify functions to allow for color selection of obstacles and rock samples.
Here is an example of how to include an image in your writeup.

![alt text][image1]

#### 1. Populate the `process_image()` function with the appropriate analysis steps to map pixels identifying navigable terrain, obstacles and rock samples into a worldmap.  Run `process_image()` on your test data using the `moviepy` functions provided to create video output of your result. 
And another! 

![alt text][image2]
### Autonomous Navigation and Mapping

#### 1. Fill in the `perception_step()` (at the bottom of the `perception.py` script) and `decision_step()` (in `decision.py`) functions in the autonomous mapping scripts and an explanation is provided in the writeup of how and why these functions were modified as they were.


#### 2. Launching in autonomous mode your rover can navigate and map autonomously.  Explain your results and how you might improve them in your writeup.  

**Note: running the simulator with different choices of resolution and graphics quality may produce different results, particularly on different machines!  Make a note of your simulator settings (resolution and graphics quality set on launch) and frames per second (FPS output to terminal by `drive_rover.py`) in your writeup when you submit the project so your reviewer can reproduce your results.**

Here I'll talk about the approach I took, what techniques I used, what worked and why, where the pipeline might fail and how I might improve it if I were going to pursue this project further.  



![alt text][image3]

# Answer

### Notebook Analysis
#### 1. Run the functions provided in the notebook on test images (first with the test data provided, next on data you have recorded). Add/modify functions to allow for color selection of obstacles and rock samples.
Here is an example of how to include an image in your writeup.

![alt text][image1]

#### 1. Populate the `process_image()` function with the appropriate analysis steps to map pixels identifying navigable terrain, obstacles and rock samples into a worldmap.  Run `process_image()` on your test data using the `moviepy` functions provided to create video output of your result. 
And another! 

![alt text][image2]
## Autonomous Navigation and Mapping

### Code 
#### perception_step()

#### decision_step()
The Rover has an internal state machine, called the 'mode', which defines distinct sets of behaviour. Switching the mode of the Rover will change its behaviour. 

This Rover has three modes; **forward**, **stop** and **escape**

##### forward mode
**forward** mode steers towards visible navigable terrain while accelerating towards a target positive velocity. The steering direction is calculated by finding the average position of the visible navigable terrain. The Rover is limited to a maximum turning angle of 15 degrees. If the Rover is below max speed, it attempts to speed up by increasing the throttle and it coasts when the maximum speed is attained. If the Rover is travelling relatively fast and has a full steering lock, then the throttle is released and a small amount of brakes is applied (see [turing circle](#Turing-circle) for a justification).

If the amount of visible navigable terrain becomes very small, the Rover is put into **stop** mode.

If the Rover has been continuously in **forward** mode but has a small velocity, then it is judged to have become trapped and is put into **escape** mode.   

##### stop mode
**stop** mode brings the Rover stationary and then rotates the Rover until a minimum amount of navigable terrain is observed, when it is put into **forward** mode.

##### escape mode
**escape** mode attempts to orientate the Rover so that it can avoid the hazard that is currently impeading its forward motion. 

### Observations

#### Turning circle
While at or near full speed, the Rover would miss small 'coves' of navigable terrain or get stuck in a 'circle of death', whereby the Rover would enter a circular clearing and then prceed to go round in circles, never taking an available exit. My theory was that the Rover's speed reduced the time that the intersting navigable terrain is visible to a point that there wasn't enough time for a radical change in direction. I countered this by modifying the behaviour step so that if the Rover was travelling at a relatively high speed and at the full steering lock then a small tap of the breaks would be applied. This momentary reduction in speed increases the likelhood of the Rover entering a 'coves' or taking an exit from a circular clearing.        

### Next Steps
Here I'll talk about the approach I took, what techniques I used, what worked and why, where the pipeline might fail and how I might improve it if I were going to pursue this project further.