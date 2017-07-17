#!/usr/bin/env python
# -*- coding: utf-8 -*-

from DEVICE import DEVICE

import time

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

    def initialize(self,channel=-1):
        self.getAndSetParameter()
        pass

    def enablePower(self,bEnable):
        if bEnable:
            self.dv.write("out_mode_05 1")
            self.Power="1"
        else:
            self.dv.write("out_mode_05 0")
            self.Power="0"
        pass

    def getPowerStatus(self):
        #s = self.dv.ask("in_mode_05")
        #if (s == "1"): return "ON"
        #else: return "OFF"
        return self.dv.ask("in_mode_05")

    def getStatus(self):
        return self.dv.ask("status")

    def getAndSetParameter(self):
        self.Power = self.getPowerStatus()
        self.T_set = self.getSetTemperature()
        self.Mode = self.getOperationMode()
        pass

    def setTemperature(self,fvalue):
        self.dv.write("out_sp_00 %.1f"%fvalue)
        pass

    def getSetTemperature(self):
        return float(self.dv.ask("in_sp_00"))

    def getInTemperature(self):
        return float(self.dv.ask("in_pv_00"))

    def getExTemperature(self):
        return float(self.dv.ask("in_pv_02"))

    def getHeaterPower(self):
        return float(self.dv.ask("in_pv_01"))

    def setOperationMode(self,sMode):
        if (sMode == "int"):
            self.dv.write("out_mode_04 0")
            self.Mode = "int"
        elif (sMode == "ext"):
            self.dv.write("out_mode_04 1")
            self.Mode = "ext"
        else: print("Unknown mode: %s"%sMode)
        pass

    def getOperationMode(self):
        if (self.dv.ask("in_mode_04") == "0"):
            return("int")
        else: return("ext")

    def close(self):
        self.dv.close()
        pass



    def output(self,  show = True):
        sMode = self.Mode
        bPower = self.Power
        if show:
            print("Julabo:")
            print("Mode: " + sMode)
            if bPower == "1":
                print("Power: \033[32m ON \033[0m")
            else:
                print("Power: \033[31m OFF \033[0m")
        fTset = self.getSetTemperature()
        fTin = self.getInTemperature()
        try:
            fTex = self.getExTemperature()
        except ValueError:
            fTex = 9999
        fHeat = self.getHeaterPower()
        if show:
            print("T_set = %.1f°C"%fTset + "\t" + "Heater Power = %.1f "%fHeat)
            print("T_in = %.1f°C"%fTin + "\t" + "T_ex = %.1f°C"%fTex)

        return([["Mode","Power","Tset[C]","Tin[C]","Tex[C]","Pheat[]"],[str(sMode),str(bPower),str(fTset),str(fTin),str(fTex),str(fHeat)]])

    def interaction(self):
        print("1: enable Power")
        print("2: change Mode")
        print("3: set new Temperature")
        x = raw_input("Number? \n")
        while x != "1" and x != "2" and x != "3" :
             x = raw_input("Possible Inputs: 1,2 or 3! \n")
        if x == "1":
            bO = raw_input("Please enter ON or OFF! \n")
            if bO == "ON" or bO == "on":
                self.enablePower(1)
            elif bO == "OFF" or bO == "off":
                self.enablePower(0)
            else:
                pass
        elif x == "2":
            sM = raw_input("choose: int or ext \n")
            self.setOperationMode(sM)
        elif x == "3":
            fT = raw_input("Please enter new Temperature in °C \n")
            self.setTemperature(float(fT))
            time.sleep(0.5)
