#!/usr/bin/env python
# -*- coding: utf-8 -*-

from DEVICE import DEVICE

class JULABO:
    dv = None
    T_set = None
    Power = None
    Mode = None

    def __init__(self,kind,adress,port):
        self.dv = DEVICE(kind=kind, adress=adress, port=port)
        self.getAndSetParameter()

    def userCmd(self,cmd):
    	print "userCmd: %s" % cmd
    	return self.dv.ask(cmd)

    def initialize(self,channel):
        self.getAndSetParameter()
        pass

    def enablePower(self,bEnable):
        if bEnable:
            self.dv.write("out_mode_05 1")
            self.Power=1
        else:
            self.dv.write("out_mode_05 0")
            self.Power=0
        pass

    def getPowerStatus(self):
        s = self.dv.ask("in_mode_05")
        if (s == "1"): return "ON"
        else: return "OFF"

    def getStatus(self):
        return self.dv.ask("status")

    def getAndSetParameter(self):
        self.Power = self.getPowerStatus()
        self.T_set = self.getSetTemperature()
        self.Mode = self.getOperationMode()
        pass

    def setTemperature(self,fvalue):
        self.dv.write("out_sp_00 %.2f")%fvalue
        pass

    def getSetTemperature(self):
        return float(self.dv.ask("in_sp_00"))

    def getInTemperature(self):
        return float(self.dv.ask("in_pv_00"))

    def getExTemperature(self):
        return float(self.dv.ask("in_pv_02"))

    def getHeaterPower(self):
        return(self.ask("in_pv_01"))

    def setOperationMode(self,sMode):
        if (sMode == "int"): self.dv.write("out_mode_04 0")
        elif (sMode == "ext"): self.dv.write("out_mode_04 1")
        else: print("Unknown mode: %s"%sMode)
        pass

    def getOperationMode(self):
        if (self.dv.ask("in_mode_04") == "0"):
            return("int")
        else: return("ext")

    def close(self):
        self.dv.close()
        pass
