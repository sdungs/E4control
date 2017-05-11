#!/usr/bin/env python
# -*- coding: utf-8 -*-

from DEVICE import DEVICE
from time import sleep

class HP4284A:
    dv = None

    def __init__(self,kind,adress,port):
        self.dv = DEVICE(kind=kind, adress=adress, port=port)

    def userCmd(self,cmd):
        print "userCmd: %s" % cmd
        return self.dv.ask(cmd)

    def initialize(self):
        #self.dv.write("*RST")
        self.dv.write(":DISP:PAGE MEAS");
        self.dv.write(":FUNC:IMP:RANG:AUTO ON");
        self.dv.write(":BIAS:STAT OFF");
        self.dv.write(":BIAS:VOLT 0");
        self.dv.write(":TRIG:DEL MIN");
        self.dv.write(":INIT:CONT ON");
        self.dv.write(":FORM ASC");
        self.dv.write(":MEM:DIM DBUF,1");
        self.dv.write(":FUNC:DEV1:MODE OFF");
        self.dv.write(":FUNC:DEV2:MODE OFF");
        self.dv.write(":MEM:CLE DBUF");
        self.dv.write(":CORR:LENG 1");
        self.dv.write(":AMPL:ALC ON");
        self.setFrequency(10000)
        self.setVoltage(0.050)
        self.setMeasurementMode("CPD")
        self.setTriggerMode("BUS")
        self.setIntegrationTimeAndAveragingRate("LONG",1)
        pass

    def getValues(self):
        v = self.dv.ask("*TRG")
        C = float(v[0:12])
        R = float(v[13:25])
        return [C,R]

    def getR(self):
        v = self.getValues()
        return v[1]

    def getC(self):
        v = self.getValues()
        return v[0]

    def setFrequency(self, fFreq):
        self.dv.write(":FREQ %f"%fFreq)
        pass

    def getFrequency(self):
        return float(self.dv.ask(":FREQ?"))

    def setOpenCorrection(self, bOC):
        if (bOC == True): self.dv.write(":CORR:OPEN:STAT ON")
        else : self.dv.write(":CORR:OPEN:STAT OFF")
        pass

    def setLoadCorrection(self, bLC):
        if (bLC == True): self.dv.write(":CORR:LOAD:STAT ON")
   	else : self.dv.write(":CORR:LOAD:STAT OFF")
        pass

    def setShortCorrection(self, bSC):
        if (bSC == True): self.dv.write(":CORR:SHOR:STAT ON")
   	else : self.dv.write(":CORR:SHOR:STAT OFF")
        pass

    def setMeasurementMode(self, sMode):
        if (sMode == "CPD"): self.dv.write(":FUNC:IMP CPD")
        elif (sMode == "CPRP"): self.dv.write(":FUNC:IMP CPRP")
        elif (sMode == "CSD"): self.dv.write(":FUNC:IMP CSD")
        elif (sMode == "CSRS"): self.dv.write(":FUNC:IMP CSRS")
        else: print("Setting measurement mode failed!")
        pass

    def setTriggerMode(self, sMode):
        if (sMode == "INT"): self.dv.write(":TRIG:SOUR INT")
        elif (sMode == "EXT"): self.dv.write(":TRIG:SOUR EXT")
        elif (sMode == "BUS"): self.dv.write(":TRIG:SOUR BUS")
        elif (sMode == "HOLD"): self.dv.write(":TRIG:SOUR HOLD")
        else: print("Setting trigger mode failed!")
        pass

    def setVoltage(self, sVolt):
        self.dv.write(":VOLT %f V"%sVolt)
        pass

    def setIntegrationTimeAndAveragingRate(self, sType, iAR):
        if (sType == "SHOR"): self.dv.write(":APER SHOR,%i"%iAR)
        elif (sType == "MED"): self.dv.write(":APER MED,%i"%iAR)
        elif (sType == "LONG"): self.dv.write(":APER LONG,%i"%iAR)
        else: print("Setting ITVR failed!")
        pass

    def reset(self):
        self.dv.write("*RST")
        pass

    def close(self):
        self.dv.close()
