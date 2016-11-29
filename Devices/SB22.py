#!/usr/bin/env python
# -*- coding: utf-8 -*-

from DEVICE import DEVICE

class SB22:
    dv = None
    T_set = None
    H_set = None
    Power = None
    D2 = None
    D3 = None
    D4 = None
    D5 = None
    D6 = None
    D7 = None
    D8 = "0"
    D9 = "0"
    D10 = "0"
    D11 = "0"
    D12 = "0"
    D13 = "0"
    D14 = "0"
    D15 = "0"
    D16 = "0"

    def __init__(self,kind,adress,port):
        self.dv = DEVICE(kind=kind, adress=adress, port=port)
        self.getAndSetParameter()

    def userCmd(self,cmd):
    	print "userCmd: %s" % cmd
    	return self.dv.ask(cmd)

    def initialize(self,channel):
        self.getAndSetParameter()
        pass

    def generateChecksum(self,cmd):
        B = 0
        for i in cmd:
            J = ord(i)
            B = B - J
            if (B<-255):B = B + 256
        B = 256 + B
        J = B/16
        if (J<10): J = J + 48
        else: J = J + 55
        K = B % 16
        if (K<10): K = K + 48
        else: K = K + 55
        result = chr(J) + chr(K)
        return result

    def updateChanges(self):
        line= chr(02)+"1T%sF%sR%s%s%s%s%s%s%s000000000"%(self.T_set,self.H_set,self.Power,self.D2,self.D3,self.D4,self.D5,self.D6,self.D7)
        pn = self.generateChecksum(line)
        cmd = "%s%s"%(line,pn)+chr(03)
        self.dv.write(cmd)
        pass

    def enablePower(self,bEnable):
        if bEnable: self.Power="1"
        else: self.Power="0"
        self.updateChanges()
        pass

    def getStatus(self):
        return self.dv.ask(chr(02)+"1?8E\3"+chr(03))

    def getAndSetParameter(self):
        s = self.getStatus()
        if (s.find("#") >= 0):
            p = s.split("#")[1]
        else:
            p = s.split("$")[1]
        line = p[p.find("R")+1:p.find("R")+8]
        self.Power = line[0]
        self.D2 = line[1]
        self.D3 = line[2]
        self.D4 = line[3]
        self.D5 = line[4]
        self.D6 = line[5]
        self.D7 = line[6]
        self.T_set = p[p.find("T")+1:p.find("F")]
        self.H_set = p[p.find("F")+1:p.find("R")]
        pass

    def setTemperature(self,fvalue):
        self.T_set = "%.1f"%fvalue
        self.updateChanges()
        pass

    def getSetTemperature(self):
        return float(self.T_set)

    def getTemperature(self):
        s = self.getStatus()
        if (s.find("#") >= 0):
            p = s.split("#")[0]
        else:
            p = s.split("$")[0]
        v = p[p.find("T")+1:p.find("F")]
        return float(v)

    def setHumidity(self,fvalue):
        self.H_set = "%.1f"%fvalue
        self.updateChanges()
        pass

    def getSetHumidity(self):
        return int(self.H_set)

    def getHumidity(self):
        s = self.getStatus()
        if (s.find("#") >= 0):
            p = s.split("#")[0]
        else:
            p = s.split("$")[0]
        v = p[p.find("F")+1:p.find("P")]
        return int(v)

    def getError(self):
        s = self.getStatus()
        if (s.find("#") >= 0):
            v = s[s.find("#")+1:p.find("T")]
        else:
            v = s[s.find("$")+1:p.find("T")]
        return v

    def setOperationMode(self,sMode):
        if (sMode == "climate"): self.D2 = "0"
        elif (sMode == "normal"): self.D2 = "1"
        else: print("Unknown mode: %s"%sMode)
        pass

    def getOperationMode(self):
        if (self.D2 == "1"): mode = "climate"
        else: mode = "normal"
        return mode

    def enableProtectionSystem(self, bEnable):
        if bEnable: self.D3 = "1"
        else: self.D3 = "0"
        pass

    def enableDewPointExtension(self, bEnable):
        if bEnable: self.D4 = "1"
        else: self.D4 = "0"
        pass

    def enableCapacitiveHumidity(self, bEnable):
        if bEnable: self.D5 = "1"
        else: self.D5 = "0"
        pass

    def enableEngerySavingMode(self, bEnable):
        if bEnable: self.D6 = "1"
        else: self.D6 = "0"
        pass

    def enableAdjustableAirFanSpeed(self, bEnable):
        if bEnable: self.D7 = "1"
        else: self.D7 = "0"
        pass

    def close(self):
        self.dv.close()
        pass
