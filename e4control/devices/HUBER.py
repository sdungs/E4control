# -*- coding: utf-8 -*-

import time

from .device import Device


class HUBER(Device):
    T_set = None
    Power = None

    def __init__(self, connection_type, host, port):
        super(HUBER, self).__init__(connection_type=connection_type, host=host, port=port)
        self.getAndSetParameter()

    def initialize(self):
        self.getAndSetParameter()

    def getAndSetParameter(self):
        self.T_set = self.getSetTemperature()
        self.Power = self.getPowerStatus()

    def getPowerStatus(self):
        sPower = self.ask('CA?')
        return bool(sPower[7])

    def enablePower(self, sBool):
            self.write('CA@{:05.0f}'.format(sBool))
            self.Power = sBool

    def getSetTemperature(self):
        sTemp = self.ask('SP?')
        return float('{:+06.2f}'.format(float(sTemp[3:])/100))

    def getInTemperature(self):
        sTemp = self.ask('TI?')
        return float('{:+06.2f}'.format(float(sTemp[3:])/100))

    def setTemperature(self, Tset):
        self.write('SP@{:+06.0f}'.format(100 * Tset))
        pass

    def output(self, show = True):
        bPower = self.Power
        if show:
            print('Minichiller:')
            if bPower:
                print('Power: \033[32m ON \033[0m')
            else:
                print('Power: \033[31m OFF \033[0m')
        fTset = self.getSetTemperature()
        fTin = self.getInTemperature()
        if show:
            print('T_set = {:.2f}'.format(fTset) + '\t' + 'T_in = {:.2f}'.format(fTin))
        return([['Power', 'Tset[C]', 'Tin[C]'], [ str(bPower), str(fTset), str(fTin)]])

    def interaction(self):
        print('1: enable Power')
        print('2: set new Temperature')
        x = input('Number? \n')
        while x != '1' and x != '2':
            x = input('Possible Inputs: 1 or 2! \n')
        if x == '1':
            bO = input('Please enter ON or OFF! \n')
            if bO == 'ON' or bO == 'on':
                self.enablePower(True)
            elif bO == 'OFF' or bO == 'off':
                self.enablePower(False)
            else:
                pass
        elif x == '2':
            fT = input('Please enter new Temperature in °C \n')
            self.setTemperature(float(fT))
            time.sleep(0.5)

