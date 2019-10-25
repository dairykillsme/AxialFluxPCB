from Alternator import *
import matplotlib.pyplot as plt

def CalcResistance(length, width, weight):
    resistivity = 1.7 * 1e-6 # Resistivity of copper in Ohms/cm
    lamdaCopper = 3.9 * 1e-3 # Lambda of copper in Ohms / Ohm / cm
    height = 1.37 * weight * 0.00254 # weight -> mils -> cm

    return resistivity * (length * .1) / (height * width * .1) * (1 - 2*lamdaCopper)

alt = Alternator()

# INITIAL PARAMETER LIST
# ONLY CHANGE THIS PART OF THE FILE
targetEMF = 25
targetRPM = 500
# END PARAMETER LIST

radius = []
emfs = []
emfs_riemann = []
emfs_riemann_round = []
emfs_round = []
resistances = []
powers = []

alt.simulate()
emf = alt.getEMF(targetRPM)
alt.closeSimulation()

while emf < targetEMF:
    initialEMF = emf
    initalInnerRadius = alt.innerRadius
    alt.numWindings += alt.numLayers
    coilAdded = False
    while alt.innerRadius < alt.outerRadius:
        if alt.build(True):
            alt.simulate()
            emf = alt.getEMF(targetRPM)
            alt.closeSimulation()
            if emf > initialEMF:
                coilAdded = True
                break
        else:
            alt.innerRadius *= 1.1

    if not coilAdded:
        alt.innerRadius = initalInnerRadius
        alt.numWindings -= alt.numLayers
        alt.outerRadius *= 1.1

    coilLength = alt.build(True)
    alt.simulate()
    emf = alt.getEMF(targetRPM)
    emf_rieman = alt.getEMFRieman(targetRPM)
    emf_round = alt.getEMFRound(targetRPM, 5)
    emf_riemann_round = alt.getEMFRiemannRound(targetRPM)
    resistance = alt.numPhases * CalcResistance(coilLength, alt.windingWidth, 2)
    alt.closeSimulation()

    emfs.append(emf)
    radius.append(alt.outerRadius)
    emfs_riemann.append(emf_rieman)
    emfs_riemann_round.append(emf_riemann_round)
    emfs_round.append(emf_round)
    resistances.append(resistance)
    powers.append(emf_rieman**2/(4 * resistance))

#plt.plot(radius, emfs, 'r')
plt.plot(radius, emfs_riemann, 'g')
plt.plot(radius, emfs_riemann_round, 'b')
plt.plot(radius, powers, 'r')
#plt.plot(radius, emfs_round, 'k')
plt.xlabel('Radius (mm)')
plt.ylabel('Output Voltage (V)')
plt.legend(['Trapezoidal Magnets', 'Round Magnets'])
plt.show()

rpms = [];
emfs.clear()
for rpm in range(0, 3000):
    rpms.append(rpm)
    emfs.append(alt.getEMF(rpm))

plt.plot(radius, resistances)
plt.xlabel('Radius (mm)')
plt.ylabel('Resistance (Ohm)')
plt.show()

print(alt.outerRadius)
print(alt.innerRadius)
print(alt.numWindings)
