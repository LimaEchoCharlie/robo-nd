import numpy as np
import csv

class current_frame_fidelity:
    def __init__(self):
        self.firsttime = True
        self.csvname ='frame_fidelity_stats.csv'

    def save_frame(self, Rover, navigable_world):
        if self.firsttime:
            self.firsttime = False
            with open(self.csvname, 'w', newline='') as csvfile:
                csv.writer(csvfile).writerow(["good_nav_pix", "tot_nav_pix", "fidelity", "Rover.pitch", "Rover.roll"])

        good_nav_pix = np.count_nonzero((Rover.ground_truth[navigable_world[1], navigable_world[0], 1] > 0))
        tot_nav_pix = len(navigable_world[0])
        fidelity = 0 if tot_nav_pix == 0 else round(100*good_nav_pix/(tot_nav_pix), 1)
        with open(self.csvname, 'a', newline='') as csvfile:
            csv.writer(csvfile).writerow([good_nav_pix,tot_nav_pix, fidelity, Rover.pitch, Rover.roll])
