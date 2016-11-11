#!/usr/bin/env python
# -*- coding: utf-8 -*-

from DEVICE import DEVICE

class HMP4040:
    dv = None

    def __init__(self,adress,port):
        self.dv = DEVICE(kind="lan", adress=adress, port=port)

    def userCmd(self,cmd):
        print "userCmd: %s" % cmd
        return self.dv.ask(cmd)

    def setVoltageLimit(self,iOutput,fValue):
        self.dv.write("INST OUT%i"%iOutput)
        self.dv.write("VOLT:PROT %f"%fValue)

    def setVoltage(self,iOutput,fValue):
        self.dv.write("INST OUT%i"%iOutput)
        self.dv.write("VOLT %f"%fValue)

    def setCurrent(self,iOutput,fValue):
        self.dv.write("INST OUT%i"%iOutput)
        self.dv.write("CURR %f"%fValue)

    def getVoltage(self,iOutput):
        self.dv.write("INST OUT%i"%iOutput)
        return float(self.dv.ask("MEAS:VOLT?"))

    def getCurrent(self,iOutput):
        self.dv.write("INST OUT%i"%iOutput)
        return float(self.dv.ask("MEAS:CURR?"))

    def enableOutput(self,iOutput,bValue):
        if bValue == True:
            self.dv.write("INST OUT%i"%iOutput)
            self.dv.write("OUT 1")
        elif bValue == False:
            self.dv.write("INST OUT%i"%iOutput)
            self.dv.write("OUT 0")

    def close(self):
        self.dv.close()
