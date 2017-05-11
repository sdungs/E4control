#!/usr/bin/env python
# -*- coding: utf-8 -*-

from DEVICE import DEVICE
import math

class K2000:
    dv = None
    #mode = None

    def __init__(self,kind,adress,port):
        self.dv = DEVICE(kind=kind, adress=adress, port=port)
        self.initialize("T")

    def userCmd(self,cmd):
    	print "userCmd: %s" % cmd
    	return self.dv.ask(cmd)


    def initialize(self, sMode):
        #self.dv.write(":SYTS:BEEP:STAT OFF")
        if (sMode == "H"):
            self.setKind("DCV")
            self.setRange("RO")
            #self.mode = "H"
            pass
        elif (sMode == "T2W"):
            self.setKind("OHM")
            self.setRange("R2")
            #self.mode = "T2W"
            pass
        elif (sMode == "T"):
            self.setKind("OHM4")
            self.setRange("R2")
            #self.mode = "T4W"
            pass
        else:
            print("Initializing not possible: Unknown mode!")
        pass

    def setKind(self, sKind):
        if (sKind == "DCV"): self.dv.write("F0X")
        elif (sKind == "ACV"): self.dv.write("F1X")
        elif (sKind == "OHM"): self.dv.write("F2X")
        elif (sKind == "OHM4"): self.dv.write("F9X")
        elif (sKind == "DCI"): self.dv.write("F3X")
        elif (sKind == "ACI"): self.dv.write("F4X")
        elif (sKind == "dBV"): self.dv.write("F5X")
        elif (sKind == "F"): self.dv.write("F7X")
        elif (sKind == "T"): self.dv.write("F8X")
        pass

    def setRange(self,sRange):
        if (sRange == "R0") : self.dv.write("R0X")
        elif (sRange == "R1") : self.dv.write("R1X")
        elif (sRange == "R2") : self.dv.write("R2X")
        elif (sRange == "R3") : self.dv.write("R3X")
        elif (sRange == "R4") : self.dv.write("R4X")
        elif (sRange == "R5") : self.dv.write("R5X")
        elif (sRange == "R6") : self.dv.write("R6X")
        elif (sRange == "R7") : self.dv.write("R7X")

    def getStatus(self):
        return self.dv.ask("U0X")

    def getKind(self):
        self.dv.ask("U0X")
	s = self.dv.read()
        return s[0:4]

    def getValue(self):
        self.dv.ask("U0X")
	v = self.dv.read()
        return float(v[4:])

    def getResistance(self, channel):
        self.dv.write("N%iX"%channel)
        fR = self.getValue()
        return fR

    def getVoltage(self, channel):
        self.dv.write("N%iX"%channel)
        fV = self.getValue()
        return fV

    def getTempPT100(self, channel):
        a = 3.90802E-3
        b = -5.802E-7
        R0 = 100.00
        R = self.getResistance(channel)
        return (-a/(2*b)-math.sqrt(R/(R0*b)-1/b+(a/(2*b))*(a/(2*b))))

    def getTempPT1000(self, channel):
        a = 3.90802E-3
        b = -5.802E-7
        R0 = 1000.00
        R = self.getResistance(channel)
        return (-a/(2*b)-math.sqrt(R/(R0*b)-1/b+(a/(2*b))*(a/(2*b))))

    def getTempPT1000all(self):
        a = 3.90802E-3
        b = -5.802E-7
        R0 = 1000.00
        Ts = []
        i = 1
        while i <= 5:
            R = self.getResistance(i)
            Ts.append(-a/(2*b)-math.sqrt(R/(R0*b)-1/b+(a/(2*b))*(a/(2*b))))
        return(Ts)

    def getHumidity(self, fTemp, channel):
        a=0.0315
        b=0.826
        V = self.getVoltage(channel)
        return ((V-b)/a)/(1.0546-0.00216*fTemp);

    def restart(self):
        self.dv.write("L0X")
        pass

    def close(self):
        self.dv.close()
        pass
