#!/usr/bin/env python
# -*- coding: utf-8 -*-

from DEVICE import DEVICE
from time import sleep

class K487:
    dv = None

    def __init__(self,kind,adress,port):
        self.dv = DEVICE(kind=kind, adress=adress, port=port)

    def userCmd(self,cmd):
        print "userCmd: %s" % cmd
        return self.dv.ask(cmd)

    def initialize(self):
        self.dv.write("G0O0C1X")
        self.dv.write("L4X") 
        pass

    def setVoltage(self,fsetValVolts):
        self.dv.write("V%.3f,1,1X"%fsetValVolts)
        pass

    def enableOutput(self,bEnable):
        if bEnable == True:
            self.dv.write("O1X")
        elif bEnable == False:
            self.dv.write("O0X")
        pass

    def getVoltage(self):
        v = self.dv.ask("U8X")
        fv = fv = float(v[v.find("=")+1:v.find("E")])*10**float(v[v.find("E")+1:v.find("E")+4])
        return fv

    def getCurrent(self):
        v = self.dv.ask("U6X")
        fv = float(v[v.find("=")+1:v.find("E")])*10**float(v[v.find("E")+1:v.find("E")+4])
        return fv

    def setRange(self,sRange):
        if (sRange == "R0") :
            self.dv.write("R0X")
            self.dv.write("C2X")
            pass
        elif (sRange == "R1") :
            self.dv.write("R1X")
            self.dv.write("C2X")
            pass
        elif (sRange == "R2") :
            self.dv.write("R2X")
            self.dv.write("C2X")
            pass
        elif (sRange == "R3") :
            self.dv.write("R3X")
            self.dv.write("C2X")
            pass
        elif (sRange == "R4") :
            self.dv.write("R4X")
            self.dv.write("C2X")
            pass
        elif (sRange == "R5") :
            self.dv.write("R5X")
            self.dv.write("C2X")
            pass
        elif (sRange == "R6") :
            self.dv.write("R6X")
            self.dv.write("C2X")
            pass
        elif (sRange == "R7") :
            self.dv.write("R7X")
            self.dv.write("C2X")
            pass
        else: print("No new range set!")
        pass

    def setTrigger(self, sTrigger):
        pass

    def setFilterMode(self, sFilter):
        if (sTrigger == "P0") : self.dv.write("P0X")
        elif (sTrigger == "P1") : self.dv.write("P1X")
        elif (sTrigger == "P2") : self.dv.write("P2X")
        elif (sTrigger == "P3") : self.dv.write("P3X")
        else: print("No new filter set!")
        pass

    def rampVoltage(self,fVnew,iSteps,iDelay):
        V = self.getVoltage()
        V = round(V,4)
        if abs(fVnew-V)<1:
            self.setVoltage(fVnew)
            return
        s = 1
        iSteps = int(iSteps+1)
        Vstep = float((fVnew-V)/(iSteps-1))
        while s < (iSteps):
            self.setVoltage((Vstep*s+V))
            sleep(iDelay)
            print "Voltage: %.4f V"%(Vstep*s+V)
            s += 1
            pass

    def reset(self):
        self.dv.write("L0X")

    def close(self):
        self.dv.close()
