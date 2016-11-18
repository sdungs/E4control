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

    def initialize(self,channel):
        pass

    def getVoltage(self,channel):
        v = self.dv.ask("U%i"%channel)
        v = v.replace("U%i"%channel,"")
        fv=float(v[:-3])*10**float(v[-3:])
        return fv

    def getCurrent(self,channel):
        v = self.dv.ask("I%i"%channel)
        v = v.replace("I%i"%channel,"")
        fv = float(v[:-3])*10**float(v[-3:])
        return fv

    def getVoltageLimit(self,channel):
        voltLim = self.dv.ask("M%i"%channel)
        voltLim = voltLim.replace("M%i"%channel,"")
        return float(voltLim)

    def getCurrentLimit(self,channel):
        currentLim = self.dv.ask("N%i"%channel)
        currentLim = currentLim.replace("N%i"%channel,"")
        return float(currentLim)

    def getSetVoltage(self,channel):
        sV = self.dv.ask("D%i"%channel)
        sV = sV.replace("D%i"%channel,"")
        fsV = float(sV[:-3])*10**float(sV[-3:])
        return fsV

    def getRampSpeed(self,channel):
        rS = self.dv.ask("V%i"%channel)
        rS = rS.replace("V%i"%channel,"")
        return int(rS)

    def setVoltage(self,fvalVolts,channel):
        self.dv.write("D%i=%4.2f"%(channel,fvalVolts))
      	pass

    def setRampSpeed(self,rampSpeed,channel):
        if rampSpeed < 2 or rampSpeed > 255:
            print("Set RampSpeed is out off range!")
            pass
        else:
            self.dv.ask("V%i=%3i"%(channel,rampSpeed))
            pass

    def rampVoltage(self,fVnew,iSteps,iDelay,channel): #channel include
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
            print "Voltage: %.2f"%(Vstep*s+V)
            s += 1
            pass

    def getStatus(self,channel):
        s = self.dv.ask("S%i"%channel)
        s = s.replace("S%i="%channel,"")
        return s

    def startRampU(self,channel):
        s = self.dv.ask("G%i"%channel)
        s = s.replace("G%i"%channel,"")
        print(s)
        pass

    def close(self):
        self.dv.close()
        pass
