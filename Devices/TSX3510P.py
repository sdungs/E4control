#!/usr/bin/env python
# -*- coding: utf-8 -*-

from DEVICE import DEVICE

class TSX3510P:
    dv = None

    def __init__(self,kind,adress,port):
        self.dv = DEVICE(kind=kind, adress=adress, port=port)

    def userCmd(self,cmd):
        print "userCmd: %s" % cmd
        return self.dv.ask(cmd)

    def initialize(self):
        pass

    def setVoltageLimit(self,fValue):
        self.dv.write("OVP %f"%fValue)

    def getVoltageLimit(self):
	ovp = self.dv.ask("OVP?")
	return float(ovp[4:])

    def setVoltage(self,fValue):
        self.dv.write("V %0.2f"%fValue)

    def setCurrent(self,fValue):
        self.dv.write("I %0.2f"%fValue)

    def getVoltage(self):
        v = self.dv.ask("VO?")
	return float(v[:v.find("V")])

    def getVoltageSet(self):
        v = self.dv.ask("V?")
	return float(v[2:])

    def getCurrent(self):
        v = self.dv.ask("IO?")
	return float(v[:v.find("A")])

    def getCurrentSet(self):
        v = self.dv.ask("I?")
	return float(v[2:])

    def getPower(self):
        v = self.dv.ask("POWER?")
        return float(v[:v.find("W")])

    def enableOutput(self,bValue):
        if bValue == True:
            self.dv.write("OP 1")
        elif bValue == False:
            self.dv.write("OP 0")

    def close(self):
        self.dv.close()


    def output(self, show = True):
        bOutput = self.getEnableOutput()
        fVlim = self.getVoltageLimit()
        fVoltage = self.getVoltage()
        fCurrent = self.getCurrent()
        fPower = self.getPower()
        if show:
            print("TSX3510P:")
            if a == "1":
                print("CH %i:"%i + "\t" + "\033[32m ON \033[0m")
            else:
                print("CH %i:"%i + "\t" + "\033[31m OFF \033[0m")
            print("Voltage = %0.1fV"%b + "\t" + "Current = %0.3fA"%c)
        values = [str(bOutput),str(fVlim),str(fVoltage),str(fCurrent),str(fPower)]
        header = ["Output","OVP[V]","U[V]","I[A]","P[W]"]
        return([header,values])

    def interaction(self):
        print("1: enable Output")
        print("2: set OVP")
        print("3: set Voltage")
        print("4: set Current")
        x = raw_input("Number? \n")
        while x != "1" and x != "2" and x != "3" and x != "4":
             x = raw_input("Possible Inputs: 1,2,3 or 4! \n")
        if x == "1":
            bO = raw_input("Please enter ON or OFF! \n")
            if bO == "ON" or bO == "on":
                self.enableOutput(True)
            elif bO == "OFF" or bO == "off":
                self.enableOutput(False)
            else:
                pass
        elif x == "2":
            fOVP = raw_input("Please enter new OVP in V\n")
            self.setVoltage(channel,float(fV))
        elif x == "3":
            fV = raw_input("Please enter new Voltage in V\n")
            self.setVoltage(channel,float(fV))
        elif x == "4":
            fI = raw_input("Please enter new Current in A%i\n")
            self.setCurrent(channel,float(fI))
