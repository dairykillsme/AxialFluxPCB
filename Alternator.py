import femm
from AlternatorGeometry import *

# Function for exporting
#              0        1          2      3      4        5    6
LIST_elmt = ["  ("," (start ",") (end ",") "," (layer ",") ","))"]
# LIST_elmt = ["  (gr_line (start 131.571908 182.314571) (end 112.874456 120.68499) (angle 90) (layer Dwgs.User) (width 0.1))"]
# LIST_elmt = ["  (segment (start 118.7 106.7) (end 119.4 106.7) (width 0.25) (layer B.Cu) (net 0))"]
DICT_elmt = {"seg" : ["segment", "(width ", "(net "],
             "arc" : ["gr_arc", "(angle ", "(width "],
             "lne" : ["gr_line", "(angle ", "(width "],
             }
DICT_lyr = { "dwg" : "Dwgs.User",
             "cmt" : "Cmts.User",
             "cut" : "Edge.Cuts",
             "fcu" : "F.Cu",
             "1cu" : "In1.Cu",
             "2cu" : "In2.Cu",
             "3cu" : "In3.Cu",
             "4cu" : "In4.Cu",
             "bcu" : "B.Cu",
             }


def fncString (element, startStr, endStr, angle, layer, width):
    stingLine = ""
    """
                      0          1         2    3          4           5
    LIST_elmt = ["  ("," (start ",") (end ",") "," (layer ",") (width ","))"]
    """
    for i in range(len(LIST_elmt)):
        stingLine += LIST_elmt[i]
        if i == 0:
            stingLine += DICT_elmt[element][0]
        if i == 1:
            stingLine += startStr
        if i == 2:
            stingLine += endStr
        if i == 3:
            if element == "seg":
                stingLine += DICT_elmt[element][1]
                stringAngle = "{:.1f}".format(width)
            else:
                stingLine += DICT_elmt[element][1]
                if element == "lne":
                    stringAngle = "90"
                else:
                    stringAngle = str(angle)
            stingLine += stringAngle + ")"
        if i == 4:
            stingLine += DICT_lyr[layer]
        if i == 5:
            if element == "seg":
                stingLine += DICT_elmt[element][2]
                stingLine += str(angle)
            else:
                stingLine += DICT_elmt[element][2]
                stingLine += "{:.2f}".format(width)
    stingLine += "\n"
    return stingLine


class Alternator:
    def __init__(self):
        # INITIAL PARAMETER LIST
        # ONLY CHANGE THIS PART OF THE FILE
        # fixed dimensions
        self.innerRadius = 12.7  # Inscribing circle in  mm
        self.outerRadius = 25.4  # Inscribing circle in mm
        self.airGap = 1  # gap between a rotor and stators in mm
        # stator dimensions
        self.numStators = 9  # Number of stator coils
        self.numWindings = 24  # Number of Windings Per Coil
        self.numPhases = 3  # Number of phases
        self.numLayers = 6 # Number of layers
        self.windingWidth = 0.5  # Width of trace in mm
        self.windingBuffer = 0.6  # Width of trace +  buffer in mm
        self.pcbThickness = 1  # Thickness of PCB in mm
        self.windingType = '0.125mm'
        # rotor dimensions
        self.rotorThickness = 2  # Thickness of rotor in mm
        self.numPoles = 12  # number of poles on rotor
        self.poleSpacing = 1  # spacing of poles in mm
        self.magnetType = 'NdFeB 52 MGOe'
        # END PARAMETER LIST
        self.testPoint = Vector(0,0)
        self.__updateDimensions()


    def __updateDimensions(self):
        # CALCULATE ARC LENGTHS ALONG AVERAGE RADIUS
        self.averageRadius = (self.outerRadius + self.innerRadius) / 2
        self.centralAngleCoil = 360 / self.numStators
        self.centralAngleMagnets = 360 / self.numPoles
        self.unbufferedCoilLength = calcArcLength(self.averageRadius, self.centralAngleCoil)
        self.unbufferedMagnetLength = calcArcLength(self.averageRadius, self.centralAngleMagnets)
        # calculate buffer between trapezoid coils, then subtract from unbuffered coil length
        # buffer includes a via, space for a trace, and buffers
        self.viaDiameter = 2 * self.windingWidth
        self.coilBuffer = self.viaDiameter + self.windingWidth + 3 * self.windingBuffer
        self.coilBufferAngle = degrees(2 * asin(self.coilBuffer / (2 * self.averageRadius)))
        self.coilBufferLength = calcArcLength(self.averageRadius, self.coilBufferAngle)
        self.coilLength = self.unbufferedCoilLength - self.coilBufferLength
        # calculate buffer between permanent magnets
        self.magnetBufferAngle = degrees(2 * asin(self.poleSpacing / (2 * self.averageRadius)))
        self.magnetBufferLength = calcArcLength(self.averageRadius, self.magnetBufferAngle)
        self.magnetLength = self.unbufferedMagnetLength - self.magnetBufferLength
        # calculate area of magnet in Meters
        self.bufferedMagnetAngle = self.centralAngleMagnets - self.magnetBufferAngle
        self.outerSectorArea = 0.5 * radians(self.bufferedMagnetAngle) * (self.outerRadius * .001) ** 2
        self.innerSectorArea = 0.5 * radians(self.bufferedMagnetAngle) * (self.innerRadius * .001) ** 2
        self.magnetArea = self.outerSectorArea - self.innerSectorArea
        # coil and pole pitch, winding factor
        self.coilPitch = self.centralAngleCoil - self.coilBufferAngle / 2
        self.polePitch = self.centralAngleMagnets / 2
        self.alpha = self.coilPitch - self.polePitch
        self.windingFactor = cos(radians(self.alpha) / 2)
        self.coilsPerPhase = self.numStators / self.numPhases
        # test point
        # self.testpoint = Vector(0,0)


    def simulate(self):
        self.__updateDimensions()
        # open FEMM
        femm.openfemm()
        femm.main_maximize()

        # True Steady State
        # new Magnetostatics document

        femm.newdocument(0)

        # Define the problem type.  Magnetostatic; Units of mm; 2D planar;
        # Precision of 10^(-8) for the linear solver; a placeholder of 0 for
        # the depth dimension, and an angle constraint of 30 degrees
        femm.mi_probdef(0, 'millimeters', 'planar', 1.e-8, 0, 30)

        # Import Materials
        femm.mi_getmaterial('Air')
        femm.mi_getmaterial(self.magnetType)
        femm.mi_getmaterial(self.windingType)

        # Draw geometry
        # Coil
        for coil in range(0, self.numStators):
            corner = Vector(coil * (self.coilLength + self.coilBufferLength), 0)
            femm.mi_drawrectangle(corner.x, corner.y, corner.x + self.coilLength, corner.y + self.pcbThickness)
            femm.mi_addblocklabel(corner.x + self.coilLength / 2, corner.y + self.pcbThickness / 2)
            femm.mi_selectlabel(corner.x + self.coilLength / 2, corner.y + self.pcbThickness / 2)
            femm.mi_setblockprop(self.windingType, 1, 0, '<None>', 0, 0, self.numWindings)


        # # Upper Rotor
        for magnet in range(0, self.numPoles):
            corner = Vector(magnet * (self.magnetLength + self.magnetBufferLength), self.pcbThickness + self.airGap)
            femm.mi_drawrectangle(corner.x, corner.y, corner.x + self.magnetLength, corner.y + self.rotorThickness)
            femm.mi_addblocklabel(corner.x + self.magnetLength / 2, corner.y + self.rotorThickness / 2)
            femm.mi_selectlabel(corner.x + self.magnetLength / 2, corner.y + self.rotorThickness / 2)
            if magnet % 2 == 0:
                femm.mi_setblockprop(self.magnetType, 1, 0, '<None>', 90, 0, 0)
            else:
                femm.mi_setblockprop(self.magnetType, 1, 0, '<None>', -90, 0, 0)
            if magnet == int(self.numPoles / 2):
                self.testPoint = Vector(corner.x, 0 + self.pcbThickness / 2)

        # Lower Rotor
        for magnet in range(0, self.numPoles):
            corner = Vector(magnet * (self.magnetLength + self.magnetBufferLength), -self.airGap)
            femm.mi_drawrectangle(corner.x, corner.y, corner.x + self.magnetLength, corner.y - self.rotorThickness)
            femm.mi_addblocklabel(corner.x + self.magnetLength / 2, corner.y - self.rotorThickness / 2)
            femm.mi_selectlabel(corner.x + self.magnetLength / 2, corner.y - self.rotorThickness / 2)
            if magnet % 2 == 0:
                femm.mi_setblockprop(self.magnetType, 1, 0, '<None>', 90, 0, 0)
            else:
                femm.mi_setblockprop(self.magnetType, 1, 0, '<None>', -90, 0, 0)

        # Define an "open" boundary condition using the built-in function:
        # Add air block label outside machine
        femm.mi_makeABC()
        airLabel = Vector((self.numStators / 2) * (self.coilLength + self.coilBufferLength), 5 * (self.rotorThickness + self.airGap))
        femm.mi_addblocklabel(airLabel.x, airLabel.y)
        femm.mi_selectlabel(airLabel.x, airLabel.y)
        femm.mi_setblockprop('Air', 1, 0, '<None>', 0, 0, 0)

        # We have to give the geometry a name before we can analyze it.
        femm.mi_saveas('alternatorSim.fem')

        # Now,analyze the problem and load the solution when the analysis is finished
        femm.mi_analyze()
        femm.mi_loadsolution()

        # Now, the finished input geometry can be displayed.
        # femm.mo_zoom(self.testPoint.x - 2 * self.coilLength, self.testPoint.y - self.coilLength,
        #              self.testPoint.x + 2 * self.coilLength,
        #              self.testPoint.y + self.coilLength)
        # femm.mo_showdensityplot(1, 0, 1, 0, 'mag')

        self.fluxDensity = self.getFlux()

    def getFlux(self):
        flux = []
        offsets = []

        for i in range(200):
            offset = i * self.numPoles * self.unbufferedMagnetLength / 200
            b = femm.mo_getb(offset, self.testPoint.y)
            flux.append(b[1])
            offsets.append(offset)

        return max(flux)

    def getFluxRiemanSum(self):
        riemanSum = 0
        interval = self.magnetLength / 200

        for i in range(200):
            x = self.testPoint.x + interval * i
            pointFlux = femm.mo_getb(x, self.testPoint.y)[1]
            riemanSum += .001 * (interval * pointFlux)
        return abs(riemanSum)

    def getEMF(self, rpm):
        # EMF Calculation
        fluxPerPole = self.fluxDensity * self.magnetArea
        frequency = self.numPoles * rpm / 120
        emf = 4.44 * frequency * fluxPerPole * self.coilsPerPhase * self.numWindings * self.windingFactor
        return self.numPhases * emf

    def getEMFMultiplier(self):
        # EMF Calculation
        fluxPerPole = self.fluxDensity * self.magnetArea
        frequency = self.numPoles / 120
        emf = 4.44 * frequency * fluxPerPole * self.coilsPerPhase * self.numWindings * self.windingFactor
        return self.numPhases * emf

    def getEMFRieman(self, rpm):
        riemanSum = self.getFluxRiemanSum()
        fluxPerPole = riemanSum * .001 * (self.outerRadius - self.innerRadius)
        frequency = self.numPoles * rpm / 120
        emf = 4.44 * frequency * fluxPerPole * self.coilsPerPhase * self.numWindings * self.windingFactor
        return self.numPhases * emf

    def getEMFRiemanMultiplier(self):
        riemanSum = self.getFluxRiemanSum()
        fluxPerPole = riemanSum * .001 * (self.outerRadius - self.innerRadius)
        frequency = self.numPoles / 120
        emf = 4.44 * frequency * fluxPerPole * self.coilsPerPhase * self.numWindings * self.windingFactor
        return self.numPhases * emf

    def getEMFRound(self, rpm, radius):
        magnetArea = pi*(.001 * radius)**2
        fluxPerPole = self.fluxDensity * magnetArea
        frequency = self.numPoles * rpm / 120
        emf = 4.44 * frequency * fluxPerPole * self.coilsPerPhase * self.numWindings * self.windingFactor
        return self.numPhases * emf

    def getEMFRiemannRound(self, rpm):
        radialRiemanSum = self.getFluxRiemanSum() / 2
        fluxPerPole = radialRiemanSum * .001 * self.magnetLength / 2 * pi
        frequency = self.numPoles * rpm / 120
        emf = 4.44 * frequency * fluxPerPole * self.coilsPerPhase * self.numWindings * self.windingFactor
        return self.numPhases * emf

    def getEMFRiemannRoundMultiplier(self):
        radialRiemanSum = self.getFluxRiemanSum() / 2
        fluxPerPole = radialRiemanSum * .001 * self.magnetLength / 2 * pi
        frequency = self.numPoles / 120
        emf = 4.44 * frequency * fluxPerPole * self.coilsPerPhase * self.numWindings * self.windingFactor
        return self.numPhases * emf

    def testRieman(self):
        riemanSum = 0
        interval = self.magnetLength / 200
        b = []
        location = []

        for i in range(200):
            x = self.testPoint.x + interval * i
            location.append(x)
            pointFlux = femm.mo_getb(x, self.testPoint.y)[1]
            b.append(pointFlux)
            riemanSum += (interval * pointFlux)

        print(max(b) * self.magnetArea)
        print(.001**2 * riemanSum * (self.outerRadius - self.innerRadius))

        return location, b

    def closeSimulation(self):
        femm.closefemm()

    def build(self, supressOutput):
        self.__updateDimensions()
        strOut = ""

        numWindingsPerLayer = int(self.numWindings / self.numLayers)
        statorRadialLength = (self.outerRadius - self.innerRadius)
        centralAngle = 360 / self.numStators
        absoluteAngleLeft = 90 + centralAngle / 2
        absoluteAngleRight = 90 - centralAngle / 2
        upperInteriorAngle = centralAngle / 2
        lowerInteriorAngle = 180 - upperInteriorAngle

        # calculate base lengths and midline length
        # first calculate buffer between trapezoid coils, then project onto bases
        # buffer includes a via, space for a trace, and buffers
        viaDiameter = 2 * self.windingWidth
        coilBuffer = (viaDiameter + self.windingWidth + 3 * self.windingBuffer) / 2

        leftCoilBound = Line(Vector.polarInit(self.innerRadius, absoluteAngleLeft),
                             Vector.polarInit(self.outerRadius, absoluteAngleLeft))
        rightCoilBound = Line(Vector.polarInit(self.innerRadius, absoluteAngleRight),
                              Vector.polarInit(self.outerRadius, absoluteAngleRight))

        projectedCoilBuffer = Vector.polarInit(-coilBuffer, absoluteAngleLeft + 90)
        projectedCoilBuffer.y = 0

        leftCoilBound.shift(projectedCoilBuffer)
        rightCoilBound.shift(-projectedCoilBuffer)

        # create upper and lower coil bounds
        upperCoilBound = Line(leftCoilBound.end, rightCoilBound.end)
        lowerCoilBound = Line(leftCoilBound.start, rightCoilBound.end)

        # Set number of vias based on layers
        if self.numLayers == 4:
            interiorVias = 2
            exteriorVias = 3
        elif self.numLayers == 6:
            interiorVias = 3
            exteriorVias = 4
        else:
            raise Exception("There must be 4 or 6 layers")

        # Set spacing variables
        viaTrace = Vector.polarInit(self.viaDiameter, absoluteAngleLeft + 90)
        exteriorViaSpacing = leftCoilBound.vectorize().scale(leftCoilBound.length() / (exteriorVias + 1))
        interiorViaSpacing = Vector(0, 1).scale(
            lowerCoilBound.length() - (2 * numWindingsPerLayer + 1) * (self.windingWidth + self.windingBuffer)) / (
                                         interiorVias + 1)
        verticalWindingSpacing = Vector(0, self.windingBuffer)
        horizontalWindingSpacing = Vector(abs(self.windingBuffer / cos(radians(upperInteriorAngle))), 0)

        # # Check if vias will fit inside coil. If they do, they will also fit outside coil lengthwise
        # # First check internal by length
        requiredSpace = interiorVias * viaDiameter + (interiorVias + 1) * (self.windingBuffer - self.windingWidth)
        actualSpace = upperCoilBound.start.y - lowerCoilBound.start.y - (2 * numWindingsPerLayer * verticalWindingSpacing.y)
        if requiredSpace > actualSpace:
            return False

        # set initial start point at bottom via
        # & initialize end point variable
        startPoint = leftCoilBound.start + viaTrace + exteriorViaSpacing
        endPoint = Vector(0, 0)

        # iterate through layers and windings
        coil = Coil()
        for layer in range(0, self.numLayers):
            # assign layer name to winding
            if self.numLayers == 4:
                if layer == 0:
                    windingLayer = Winding("fcu")
                    inum = 1
                    onum = 1
                elif layer == 1:
                    windingLayer = Winding("1cu")
                    inum = 1
                    onum = 2
                elif layer == 2:
                    windingLayer = Winding("2cu")
                    inum = 2
                    onum = 2
                else:
                    windingLayer = Winding("bcu")
                    inum = 2
                    onum = 3
            else:
                if layer == 0:
                    windingLayer = Winding("fcu")
                    inum = 1
                    onum = 1
                elif layer == 1:
                    windingLayer = Winding("1cu")
                    inum = 1
                    onum = 2
                elif layer == 2:
                    windingLayer = Winding("2cu")
                    inum = 2
                    onum = 2
                elif layer == 3:
                    windingLayer = Winding("3cu")
                    inum = 2
                    onum = 3
                elif layer == 4:
                    windingLayer = Winding("4cu")
                    inum = 3
                    onum = 3
                else:
                    windingLayer = Winding("bcu")
                    inum = 3
                    onum = 4
            # Outside-In Coil
            if layer == 0 or layer == 2 or layer == 4:
                endPoint = startPoint - viaTrace
                windingLayer.addPoint(startPoint)
                windingLayer.addPoint(endPoint)
                for turn in range(0, numWindingsPerLayer):
                    for i in range(1, 5):
                        startPoint = endPoint
                        if i == 1:
                            endPoint = leftCoilBound.end + (1.5 * turn * horizontalWindingSpacing) - (
                                        turn * verticalWindingSpacing)
                        elif i == 2:
                            endPoint = rightCoilBound.end - (1.5 * turn * horizontalWindingSpacing) - (
                                        turn * verticalWindingSpacing)
                        elif i == 3:
                            endPoint = rightCoilBound.start - (turn * horizontalWindingSpacing) + (
                                        turn * verticalWindingSpacing)
                        else:
                            endPoint = leftCoilBound.start + ((turn + 1) * horizontalWindingSpacing) + (
                                        turn * verticalWindingSpacing)
                            if endPoint.x > windingLayer.points[-1].x:
                                return False
                        windingLayer.addPoint(endPoint)
                # Add last turn and interior via
                startPoint = endPoint
                internalTopLeft = leftCoilBound.end + (1.5 * numWindingsPerLayer * horizontalWindingSpacing) - (
                            numWindingsPerLayer * verticalWindingSpacing)
                internalLeftVector = internalTopLeft - startPoint
                endPoint = startPoint + leftCoilBound.vectorize().scale(self.windingBuffer) + inum * internalLeftVector / (interiorVias + 1)
                windingLayer.addPoint(endPoint)
                startPoint = endPoint
                endPoint = startPoint - viaTrace
                windingLayer.addPoint(endPoint)
                startPoint = endPoint
            # Inside-Out Coil
            else:
                endPoint = startPoint + viaTrace
                windingLayer.addPoint(startPoint)
                windingLayer.addPoint(endPoint)
                for turn in range(0, numWindingsPerLayer):
                    multiplier = numWindingsPerLayer - turn
                    for i in range(1, 5):
                        startPoint = endPoint
                        if i == 1:
                            endPoint = leftCoilBound.end + (1.5 * multiplier * horizontalWindingSpacing) - (
                                        multiplier * verticalWindingSpacing)
                        elif i == 2:
                            endPoint = rightCoilBound.end - (1.5 * multiplier * horizontalWindingSpacing) - (
                                        multiplier * verticalWindingSpacing)
                        elif i == 3:
                            endPoint = rightCoilBound.start - (multiplier * horizontalWindingSpacing) + (
                                        (multiplier - 1) * verticalWindingSpacing)
                        else:
                            endPoint = leftCoilBound.start + ((multiplier - 1) * horizontalWindingSpacing) + (
                                        (multiplier - 1) * verticalWindingSpacing)
                        windingLayer.addPoint(endPoint)
                # Add last turn and exterior via
                startPoint = endPoint
                endPoint = startPoint + onum * leftCoilBound.vectorize() / (exteriorVias + 1)
                windingLayer.addPoint(endPoint)
                startPoint = endPoint
                endPoint = startPoint + viaTrace
                windingLayer.addPoint(endPoint)
                startPoint = endPoint

            coil.addWinding(windingLayer)

        for winding in coil.windings:
            end = winding.points[0]
            for point in winding.points:
                start = end
                end = point
                strOut += fncString("seg",  # type of line
                                    "{:.6f}".format(start.x) + " " + "{:.6f}".format(-start.y),  # start point
                                    "{:.6f}".format(end.x) + " " + "{:.6f}".format(-end.y),  # end point
                                    "0",  # angle or net value
                                    winding.layer,  # layer on pcb
                                    self.windingWidth,  # track width
                                    )

        for i in range(0, self.numStators):
            rotCoil = coil.rotate(i * centralAngle)
            for winding in rotCoil.windings:
                end = winding.points[0]
                for point in winding.points:
                    start = end
                    end = point
                    strOut += fncString("seg",  # type of line
                                        "{:.6f}".format(start.x) + " " + "{:.6f}".format(-start.y),  # start point
                                        "{:.6f}".format(end.x) + " " + "{:.6f}".format(-end.y),  # end point
                                        "0",  # angle or net value
                                        winding.layer,  # layer on pcb
                                        self.windingWidth,  # track width
                                        )
        if not supressOutput:
            print(strOut)

        return True