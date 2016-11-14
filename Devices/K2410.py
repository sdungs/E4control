#!/usr/bin/env python
# -*- coding: utf-8 -*-

from DEVICE import DEVICE
from time import sleep


class K2410:
    dv = None

    def __init__(self,adress,port):
        self.dv = DEVICE(kind="gpib", adress=adress, port=port)

    def userCmd(self,cmd):
        print "userCmd: %s" % cmd
        return self.dv.ask(cmd)

    def setCurrentAutoRange(self,bsetCurrentAutoRange):
        if bsetCurrentAutoRange: self.dv.write(":SOUR:CURR:RANG:AUTO ON")
        else: self.dv.write(":SOUR:CURR:RANG:AUTO OFF")

    def setVoltageAutoRange(self,bsetVoltageAutoRange):
        if bsetVoltageAutoRange: self.dv.write(":SOUR:VOLT:RANG:AUTO ON")
        else: self.dv.write(":SOUR:VOLT:RANG:AUTO OFF")

    def setCurrentLimit(self,fIlim):
        self.dv.write(":SENSE:CURR:PROT %f"%fIlim)

    def setVoltageLimit(self,fVlim):
        self.dv.write(":SENSE:VOLT:PROT %f"%fVlim)

    def setCurrent(self,fsetI):
        self.dv.write(":SOUR:CURR %f"%fsetI)

    def setVoltage(self,fsetV):
        self.dv.write(":SOUR:VOLT %f"%fsetV)

    def enableOutput(self,bEnable):
        if bEnable == True:
            self.dv.write(":OUTPUT ON")
        elif bEnable == False:
            self.dv.write(":OUTPUT OFF")

    def getVoltage(self):
        v = self.dv.ask(":READ?")
        if not "," in v: return -999.
        return float(v.split(",")[0])

    def getCurrent(self):
        v = self.dv.ask(":READ?")
        return float(v.split(",")[1])

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
