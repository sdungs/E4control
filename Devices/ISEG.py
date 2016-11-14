#!/usr/bin/env python
# -*- coding: utf-8 -*-

from DEVICE import DEVICE

class ISEG:
    dv = None

    def __init__(self,kind,adress,port):
        self.dv = DEVICE(kind=kind, adress=adress, port=port)

    def userCmd(self,cmd):
    	print "userCmd: %s" % cmd
    	return self.dv.ask(cmd)

    def getVoltage(self,channel):
        V = self.dv.ask("U%i"%channel)
        fV=float(V[:-3])*10**float(V[-3:])
        return fV

    def getCurrent(self,channel):
        I = self.dv.ask("I%i"%channel)
        fI = float(I[:-3])*10**float(I[-3:])
        return fI

    def getVoltageLimit(self,channel):
        voltLim = self.dv.ask("M%i"%channel)
        return float(voltLim);

    def getCurrentLimit(self,channel):
        currentLim = self.dv.ask("N%i"%channel)
        return float(currentLim);

    def getSetVoltage(self,channel):
        sV = self.dv.ask("D%i"%channel)
        fsV = float(sV[:-3])*10**float(sV[-3:])
        return fsV;

    def getRampSpeed(self,channel):
        rS = self.dv.ask("V%i"%channel)
        return int(rS);

    def setVoltage(self,channel,fvalVolts):
        self.dv.write("D%i=%4.2f"%(channel,fvalVolts))
      	pass

    def setRampSpeed(self,channel,rampSpeed):
        if rampSpeed < 2 or rampSpeed > 255:
            print("Set RampSpeed is out off range!")
            pass
        else:
            self.dv.ask("V%i=%3i"%(channel,rampSpeed))
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
            print "Voltage: %.4f"%(Vstep*s+V)
            s += 1
            pass

    def getStatus(self,channel):
        s = self.dv.ask("S%i"%channel)
        return s

    def startRampU(self,channel):
        status = self.dv.ask("G%i"%channel)
        print(status)
        pass

    def close(self):
        self.dv.close()
        pass
