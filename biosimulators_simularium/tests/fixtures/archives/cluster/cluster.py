"""Copied directly from: https://www.smoldyn.org/archive/Singh_Andrews_2021/cluster.txt

    Molecules that form a cluster. Similar to cluster3D.txt.
"""

__author__ = "Steve Andrews"
__date__ = "2020-11-23"

# Smoldyn simulation of molecule clustering
import smoldyn
import matplotlib.pyplot as plt
import numpy as np


s = smoldyn.Simulation(low=[-10, -10, -10], high=[10, 10, 10])
B = s.addSpecies('B', color='blue', difc=1, display_size=0.3)
R = s.addSpecies('R', color='red', difc=0, display_size=0.3)
B.addToSolution(200)
R.addToSolution(1, pos=[0, 0, 0])
rxn = s.addReaction(name='r', subs=[B, R], prds=[R, R], rate=20)
rxn.productPlacement(method='bounce', param=0.6)
s.addOutputData('counts')
s.addCommand(cmd='molcount counts', cmd_type='E')
s.addOutputData('molecule_locations')
s.addCommand(cmd='listmols molecule_locations', cmd_type='E')
#s.setGraphics('opengl_good', 1)
s.run(10, dt=0.1)
data = s.getOutputData('counts', 0)
dataT = np.array(data).T.tolist()

locations = s.getOutputData('molecule_locations', 0)
locationsT = np.array(locations).T.tolist()
'''plt.plot(dataT[0], dataT[2], "r")
plt.xlabel("time")
plt.ylabel("cluster size")
plt.show()'''

print(np.array(locationsT).shape)
