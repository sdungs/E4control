#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import sleep

from .device import Device


class HP4284A(Device):

    def userCmd(self, cmd):
        print "userCmd: %s" % cmd
        return self.ask(cmd)

    def initialize(self):
        #self.write("*RST")
        self.write(":DISP:PAGE MEAS");
        self.write(":FUNC:IMP:RANG:AUTO ON");
        self.write(":BIAS:STAT OFF");
        self.write(":BIAS:VOLT 0");
        self.write(":TRIG:DEL MIN");
        self.write(":INIT:CONT ON");
        self.write(":FORM ASC");
        self.write(":MEM:DIM DBUF,1");
        self.write(":FUNC:DEV1:MODE OFF");
        self.write(":FUNC:DEV2:MODE OFF");
        self.write(":MEM:CLE DBUF");
        self.write(":CORR:LENG 1");
        self.write(":AMPL:ALC ON");
        self.setFrequency(10000)
        self.setVoltage(0.050)
        self.setMeasurementMode("CPD")
        self.setTriggerMode("BUS")
        self.setIntegrationTimeAndAveragingRate("LONG",1)


    def getValues(self):
        v = self.ask("*TRG")
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
        self.write(":FREQ %f"%fFreq)
        pass

    def getFrequency(self):
        return float(self.ask(":FREQ?"))

    def setOpenCorrection(self, bOC):
        if (bOC == True): self.write(":CORR:OPEN:STAT ON")
        else : self.write(":CORR:OPEN:STAT OFF")
        pass

    def setLoadCorrection(self, bLC):
        if (bLC == True): self.write(":CORR:LOAD:STAT ON")
   	else : self.write(":CORR:LOAD:STAT OFF")
        pass

    def setShortCorrection(self, bSC):
        if (bSC == True): self.write(":CORR:SHOR:STAT ON")
   	else : self.write(":CORR:SHOR:STAT OFF")
        pass

    def setMeasurementMode(self, sMode):
        if (sMode == "CPD"): self.write(":FUNC:IMP CPD")
        elif (sMode == "CPRP"): self.write(":FUNC:IMP CPRP")
        elif (sMode == "CSD"): self.write(":FUNC:IMP CSD")
        elif (sMode == "CSRS"): self.write(":FUNC:IMP CSRS")
        else: print("Setting measurement mode failed!")
        pass

    def getMeasurementMode(self):
        return(self.ask(":FUNC:IMP?"))

    def setTriggerMode(self, sMode):
        if (sMode == "INT"): self.write(":TRIG:SOUR INT")
        elif (sMode == "EXT"): self.write(":TRIG:SOUR EXT")
        elif (sMode == "BUS"): self.write(":TRIG:SOUR BUS")
        elif (sMode == "HOLD"): self.write(":TRIG:SOUR HOLD")
        else: print("Setting trigger mode failed!")
        pass

    def setVoltage(self, sVolt):
        self.write(":VOLT %f V"%sVolt)
        pass

    def getVoltage(self):
        return(self.ask(":VOLT?"))

    def setIntegrationTimeAndAveragingRate(self, sType, iAR):
        if (sType == "SHOR"): self.write(":APER SHOR,%i"%iAR)
        elif (sType == "MED"): self.write(":APER MED,%i"%iAR)
        elif (sType == "LONG"): self.write(":APER LONG,%i"%iAR)
        else: print("Setting ITVR failed!")
        pass

    def getIntegrationTimeAndAveragingRate(self):
        return(self.ask(":APER?"))

    def reset(self):
        self.write("*RST")
        pass

    def close(self):
        self.close()


    def output(self, show = True):
        print("no output")
        return([[],[]])

    def interaction(self):
        print("Nothing to do...")
