from Alternator import *
import matplotlib.pyplot as plt
alt = Alternator()
alt.outerRadius = 30.734
alt.innerRadius = 15.367
alt.numWindings = 36
alt.magnetType = 'NdFeB 52 MGOe'
alt.poleSpacing = 1

alt.simulate()

speeds = []
raw_emf = []
riemann_emf = []
round_emf = []
riemann_round_emf = []

multiplier = alt.getEMFRiemanMultiplier()
round_multiplier = alt.getEMFRiemannRoundMultiplier()

for speed in range(0, 3000):
    speeds.append(speed)
    raw_emf.append(alt.getEMF(speed))
    riemann_emf.append(multiplier * speed)
    round_emf.append(alt.getEMFRound(speed, 5))
    riemann_round_emf.append(.7 * alt.getEMFRound(speed, 5))

alt.closeSimulation()

plt.plot(speeds, raw_emf, 'r')
plt.plot(speeds, riemann_emf, 'g')
plt.plot(speeds, round_emf, 'b')
plt.plot(speeds, riemann_round_emf, 'k')
plt.xlabel('speed (RPM)')
plt.ylabel('EMF (V)')
plt.show()
