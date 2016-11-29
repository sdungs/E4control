#!/usr/bin/env python
# -*- coding: utf-8 -*-

from DEVICE import DEVICE
from time import sleep


class K2410:
    dv = None
    rampSpeed_step = 5
    rampSpeed_delay = 1 #s

    def __init__(self,kind,adress,port):
        self.dv = DEVICE(kind=kind, adress=adress, port=port)

    def userCmd(self,cmd):
        print "userCmd: %s" % cmd
        return self.dv.ask(cmd)

    def initialize(self,channel=-1):
        pass

    def setCurrentAutoRange(self,bsetCurrentAutoRange):
        if bsetCurrentAutoRange: self.dv.write(":SOUR:CURR:RANG:AUTO ON")
        else: self.dv.write(":SOUR:CURR:RANG:AUTO OFF")

    def setVoltageAutoRange(self,bsetVoltageAutoRange):
        if bsetVoltageAutoRange: self.dv.write(":SOUR:VOLT:RANG:AUTO ON")
        else: self.dv.write(":SOUR:VOLT:RANG:AUTO OFF")

    def setCurrentLimit(self,fIlim,channel=-1):
        self.dv.write(":SENSE:CURR:PROT %f"%fIlim)

    def setVoltageLimit(self,fVlim,channel=-1):
        self.dv.write(":SENSE:VOLT:PROT %f"%fVlim)

    def setCurrent(self,fIset,channel=-1):
        self.dv.write(":SOUR:CURR %f"%fIset)

    def setVoltage(self,fVset,channel=-1):
        self.dv.write(":SOUR:VOLT %f"%fVset)

    def enableOutput(self,bEnable,channel=-1):
        if bEnable == True:
            self.dv.write(":OUTPUT ON")
        elif bEnable == False:
            self.dv.write(":OUTPUT OFF")

    def getVoltage(self,channel=-1):
        v = self.dv.ask(":READ?")
        if not "," in v: return -999.
        return float(v.split(",")[0])

    def getCurrent(self,channel=-1):
        v = self.dv.ask(":READ?")
        return float(v.split(",")[1])

    def getCurrentLimit(self,channel=-1):
        v = self.dv.ask(":SENSE:CURR:PROT?")
        return float(v)

    def getVoltageLimit(self,channel=-1):
        v = self.dv.ask(":SENSE:VOLT:PROT?")
        return float(v)

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

    def rampVoltage(self,fVnew,channel=-1):
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

    def setOutputSide(self, sside):
        if (sside == "front"): self.dv.write(":ROUT:TERM FRON")
        elif (sside == "back"): self.dv.write(":ROUT:TERM REAR")
        pass

    def getOutputSide(self):
        side = self.dv.ask(":ROUT:TERM?")
        return side

    def reset(self):
        self.dv.write("*RST")

    def close(self):
        self.dv.close()
