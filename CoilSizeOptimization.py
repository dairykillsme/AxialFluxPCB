from Alternator import *

alt = Alternator()

# INITIAL PARAMETER LIST
# ONLY CHANGE THIS PART OF THE FILE
targetEMF = 5
targetRPM = 500
# END PARAMETER LIST

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

    alt.simulate()
    emf = alt.getEMF(targetRPM)
    alt.closeSimulation()

print(emf)
alt.build(False)