#!/usr/bin/env python
# -*- coding: utf-8 -*-

from DEVICE import DEVICE
from time import sleep

class K487:
    dv = None
    rampSpeed_step = 5
    rampSpeed_delay = 1 #s

    def __init__(self,kind,adress,port):
        self.dv = DEVICE(kind=kind, adress=adress, port=port)

    def userCmd(self,cmd):
        print "userCmd: %s" % cmd
        return self.dv.ask(cmd)

    def initialize(self,channel=-1):
        self.dv.write("G0O0C1X")
        #self.dv.write("L4X")
        pass

    def setVoltage(self,fsetValVolts,channel=-1):
        self.dv.write("V%.3f,1,1X"%fsetValVolts)
        pass

    def enableOutput(self,bEnable,channel=-1):
        if bEnable == True:
            self.dv.write("O1X")
        elif bEnable == False:
            self.dv.write("O0X")
        pass

    def getVoltage(self,channel=-1):
        v = self.dv.ask("U8X")
        fv = fv = float(v[v.find("=")+1:v.find("E")])*10**float(v[v.find("E")+1:v.find("E")+4])
        return fv

    def getCurrent(self,channel=-1):
        v = self.dv.ask("U6X")
        fv = float(v[v.find("=")+1:v.find("E")])*10**float(v[v.find("E")+1:v.find("E")+4])
        return fv

    def setRange(self,sRange,channel=-1):
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

    def setTrigger(self, sTrigger,channel=-1):
        pass

    def setFilterMode(self, sFilter,channel=-1):
        if (sTrigger == "P0") : self.dv.write("P0X")
        elif (sTrigger == "P1") : self.dv.write("P1X")
        elif (sTrigger == "P2") : self.dv.write("P2X")
        elif (sTrigger == "P3") : self.dv.write("P3X")
        else: print("No new filter set!")
        pass

    def setRampSpeed(self,iRampSpeed,iDelay):
        if iRampSpeed < 1 or iRampSpeed > 255:
            print("Set RampSpeed size is out off range!")
            pass
        else:
            self.rampSpeed_step = iRampSpeed
            pass
        if iDelay < 0:
            print("No negativ Delay is possible!")
            pass
        else:
            self.rampSpeed_delay = iDelay
            pass

    def getRampSpeed(self):
        return([int(self.rampSpeed_step),int(self.rampSpeed_delay)])

    def rampVoltage(self,fVnew,channel):
        V = self.getVoltage(channel)
        V = round(V,4)
        if abs(fVnew-V)<=self.rampSpeed_step:
            self.setVoltage(fVnew,channel)
            print "Voltage reached: %.2f V"%(fVnew)
            return
        else:
            self.setVoltage(V+self.rampSpeed_step*(fVnew-V)/abs(fVnew-V))
            print "Ramp Voltage: %.2f V"%(V+self.rampSpeed_step*(fVnew-V)/abs(fVnew-V))
            sleep(self.rampSpeed_delay)
            self.rampVoltage(fVnew,channel)
            pass

    def reset(self):
        self.dv.write("L0X")

    def close(self):
        self.dv.close()
