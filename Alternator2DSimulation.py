from Alternator import *
import matplotlib.pyplot as plt
alt = Alternator()

# Parameter Changes
alt.numWindings = 16
alt.numLayers = 4

alt.simulate()

speeds = []
emfs = []

for speed in range(0, 6000):
    emf = alt.getEMF(speed)
    speeds.append(speed)
    emfs.append(emf)

alt.closeSimulation()

plt.plot(speeds, emfs)
plt.xlabel('Speed (RPM)')
plt.ylabel('No Load EMF (V)')
plt.show()