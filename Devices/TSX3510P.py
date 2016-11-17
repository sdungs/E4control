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
