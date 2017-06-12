#!/usr/bin/env python
# -*- coding: utf-8 -*-

from DEVICE import DEVICE

class HMP4040:
    dv = None

    def __init__(self,kind,adress,port):
        self.dv = DEVICE(kind=kind, adress=adress, port=port)

    def userCmd(self,cmd):
        print "userCmd: %s" % cmd
        return self.dv.ask(cmd)

    def initialize(self):
        pass

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
            self.dv.write("OUTP ON")
        elif bValue == False:
            self.dv.write("INST OUT%i"%iOutput)
            self.dv.write("OUTP OFF")

    def getEnableOutput(self,iOutput):
        self.dv.write("INST OUT%i"%iOutput)
        return self.dv.ask("OUTP?")

    def close(self):
        self.dv.close()


    def output(self, show = True):
        bPower = []
        fVoltage = []
        fCurrent = []
        values = []
        if show:
            print("HMP4040:")
        i = 1
        while i <= 4:
            a = self.getEnableOutput(i)
            b = self.getVoltage(i)
            c = self.getCurrent(i)
            bPower.append(a)
            fVoltage.append(b)
            fCurrent.append(c)
            if show:
                if a == "1":
                    print("CH %i:"%i + "\t" + "\033[32m ON \033[0m")
                else:
                    print("CH %i:"%i + "\t" + "\033[31m OFF \033[0m")
                print("Voltage = %0.1fV"%b + "\t" + "Current = %0.3fA"%c)
            values.append(str(a))
            values.append(str(b))
            values.append(str(c))
            i += 1
        header = ["CH1","U1[V]","I1[A]","CH2","U2[V]","I2[A]","CH3","U3[V]","I3[A]","CH4","U4[V]","I4[A]"]
        return([header,values])

    def interaction(self):
        ch = raw_input("Choose channel! \n")
        while ch != "1" and ch != "2" and ch != "3" and ch != "4":
             ch = raw_input("Possible Channels: 1,2,3 or 4! \n")
        channel = int(ch)
        print("1: enable Output")
        print("2: set Voltage")
        print("3: set Current")
        x = raw_input("Number? \n")
        while x != "1" and x != "2" and x != "3":
             x = raw_input("Possible Inputs: 1,2 or 3! \n")
        if x == "1":
            bO = raw_input("Please enter ON or OFF! \n")
            if bO == "ON" or bO == "on":
                self.enableOutput(channel,True)
            elif bO == "OFF" or bO == "off":
                self.enableOutput(channel,False)
            else:
                pass
        elif x == "2":
            fV = raw_input("Please enter new Voltage in V for CH %i\n"%channel)
            self.setVoltage(channel,float(fV))
        elif x == "3":
            fI = raw_input("Please enter new Current in A for CH %i\n"%channel)
            self.setCurrent(channel,float(fI))
