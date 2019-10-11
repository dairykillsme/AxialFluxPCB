from Alternator import *
import matplotlib.pyplot as plt

alt = Alternator()

spacing = []
emf = []

initial_spacing = alt.poleSpacing

for i in range(10):
    space = i * 2 * initial_spacing / 10
    alt.poleSpacing = space
    alt.simulate()
    emf.append(alt.getEMFRieman(3000))
    spacing.append(space)

alt.closeSimulation()
plt.plot(spacing, emf)
plt.xlabel('Spacing (mm)')
plt.ylabel('EMF (V)')
plt.show()