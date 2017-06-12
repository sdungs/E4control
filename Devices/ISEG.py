#!/usr/bin/env python
# -*- coding: utf-8 -*-

from DEVICE import DEVICE
from time import sleep

class ISEG:
    dv = None
    rampSpeed_step = 5
    rampSpeed_delay = 1 #s

    def __init__(self,kind,adress,port):
        self.dv = DEVICE(kind=kind, adress=adress, port=port)
        self.setHardwareRampSpeed(255,1)
        self.setHardwareRampSpeed(255,2)

    def userCmd(self,cmd):
    	print "userCmd: %s" % cmd
    	return self.dv.ask(cmd)

    def initialize(self,channel=-1):
        pass

    def enableOutput(self,bEnable,channel=-1):
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

    def setCurrentLimit(self,channel):
        #just manual setting possible
        pass

    def setVoltageLimit(self,channel):
        #just manual setting possible
        pass

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

    def getHardwareRampSpeed(self,channel):
        rS = self.dv.ask("V%i"%channel)
        rS = rS.replace("V%i"%channel,"")
        return int(rS)

    def setVoltage(self,fvalVolts,channel):
        self.dv.ask("D%i=%.1f"%(channel,abs(fvalVolts)))
      	self.startRampU(channel)
	pass

    def setHardwareRampSpeed(self,iRampSpeed,channel):
        if iRampSpeed < 2 or iRampSpeed > 255:
            print("Set RampSpeed is out off range!")
            pass
        else:
            self.dv.ask("V%i=%i"%(channel,iRampSpeed))
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
        fVnew = abs(fVnew)
        V = self.getVoltage(channel)
        V = round(V,4)
        if abs(fVnew-abs(V))<=self.rampSpeed_step:
            self.setVoltage(fVnew,channel)
            print "Voltage reached: %.2f V"%(fVnew)
            return
        else:
            self.setVoltage(abs(V)+self.rampSpeed_step*(fVnew-abs(V))/abs(fVnew-abs(V)),channel)
            print "Ramp Voltage: %.2f V"%(abs(V)+self.rampSpeed_step*(fVnew-abs(V))/abs(fVnew-abs(V)))
            sleep(self.rampSpeed_delay)
            self.rampVoltage(fVnew,channel)
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


    def output(self,  show = True):
        f1Limit = self.getCurrentLimit(1) 
        f2Limit = self.getCurrentLimit(2)
        f1Voltage = self.getVoltage(1)
        f2Voltage = self.getVoltage(2)
        f1Current =  self.getCurrent(1)
        f2Current =  self.getCurrent(2)

        if show:
            print("ISEG:")
            print("CH 1:" + "\t" + "I_lim = %.2fuA"%f1Limit)
            print("Voltage = %.1fV"%f1Voltage + "\t" + "Current = %.3fuA"%f1Current)
            print("CH 2:" + "\t" + "I_lim = %.2fuA"%f2Limit)
            print("Voltage = %.1fV"%f2Voltage + "\t" + "Current = %.3fuA"%f2Current)
        return([["Ilim1[uA]","U1[V]","I1[uA]","Ilim2[uA]","U2[V]","I2[uA]"],[str(f1Limit),str(f1Voltage),str(f1Current),str(f2Limit),str(f2Voltage),str(f2Current)]])

    def interaction(self):
        ch = raw_input("Choose channel! \n")
        while ch != "1" and ch != "2":
             ch = raw_input("Possible Channels: 1 or 2! \n")
        channel = int(ch)
        print("1: set Voltage")
        x = raw_input("Number? \n")
        while x != "1":
             x = raw_input("Possible Inputs: 1! \n")
        if x == "1":
            fV = raw_input("Please enter new Voltage in V for CH %i\n"%channel)
            self.rampVoltage(float(fV),channel)
