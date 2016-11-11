#!/usr/bin/env python
# -*- coding: utf-8 -*-

from DEVICE import DEVICE

class TSX3510P:
    dv = None

    def __init__(self,adress,port):
        self.dv = DEVICE(kind="gpib", adress=adress, port=port)

    def userCmd(self,cmd):
        print "userCmd: %s" % cmd
        return self.dv.ask(cmd)

    def setVoltageLimit(self,fValue):
        self.dv.write("OVP %f"%fValue)

    def getVoltageLimit(self):
        return float(self.dv.ask("OVP?"))

    def setVoltage(self,fValue):
        self.dv.write("V %0.2f"%fValue)

    def setCurrent(self,fValue):
        self.dv.write("I %0.2f"%fValue)

    def getVoltage(self):
        return float(self.dv.ask("VO?"))

    def getVoltageSet(self):
        return float(self.dv.ask("V?"))

    def getCurrent(self):
        return float(self.dv.ask("IO?"))

    def getCurrentSet(self):
        return float(self.dv.ask("I?"))

    def getPower(self):
        return self.dv.ask("POWER?")

    def enableOutput(self,bValue):
        if bValue == True:
            self.dv.write("OP ON")
        elif bValue == False:
            self.dv.write("OP OFF")

    def close(self):
        self.dv.close()
