# The Udacity Sample Return Robot Challenge
The goal in the [NASA Sample Return Challenge](https://www.nasa.gov/directorates/spacetech/centennial_challenges/sample_return_robot/index.html) was not just to locate samples of interest but also to pick them up and return them to the starting point! In this Udacity challenge your goal is to map the entire environment, recover all the rock samples and return them to the starting point.

## 1. Optimizing Metrics: 
The primary metrics of interest are time, percentage mapped, fidelity and number of rocks found. In the best case scenario, you would map the entire environment at a very high fidelity and locate and collect all six rock samples in the minimum total amount of time. To do this you'll need to not only optimize the accuracy your mapping analysis, but also the efficiency with which you traverse the environment.

* Optimizing Map Fidelity Tip: Your perspective transform is technically only valid when roll and pitch angles are near zero. If you're slamming on the brakes or turning hard they can depart significantly from zero, and your transformed image will no longer be a valid map. Think about setting thresholds near zero in roll and pitch to determine which transformed images are valid for mapping.
* Optimizing Time Tip: Moving faster and more efficiently will minimize total time. Think about allowing for a higher maximum velocity and give your rover the brains to not revisit previously mapped areas.
* Optimizing % Mapped Tip: Think about ways you can "close" boundaries in your map. If you can do this effectively, then once you close all boundaries your map will be complete!
* Optimizing for Finding All Rocks Tip: The rocks always appear near the walls. Think about making your rover a "wall crawler" that explores the environment by always keeping a wall on its left or right. If done correctly, this optimization can help all the aforementioned metrics.

## 2. Collect Samples:

In this project you also have the capability to pick up samples using additional telemetry and command functionality that's available to you. In the drive_rover.py script you'll find the send_pickup() function:

**Define a function to send the "pickup" command**
```
def send_pickup():
    print("Picking up")
    pickup = {}
    sio.emit(
        "pickup",
        pickup,
        skip_sid=True)
    eventlet.sleep(0)
```
You can monitor whether or not you are close enough to pick up a rock sample with the Rover.near_sample flag, which will be updated with each new batch of telemetry and will be set to 1 if you are near a rock sample. You should be stopped in order to pick up a rock, so if you are in a state where Rover.near_sample == 1 and Rover.vel == 0 you can set the Rover.pick_up flag to True and the robotic arm will be triggered into action using the following code within the telemetry():

**If in a state where want to pickup a rock send pickup command**
```
if Rover.send_pickup and not Rover.picking_up:
    send_pickup()
    # Reset Rover flags
    Rover.send_pickup = False
```
Once you have collected all six rock samples, return them to the starting point and you have successfully completed the Udacity Robotics Sample Return Challenge!
