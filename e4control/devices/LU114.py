# -*- coding: utf-8 -*-
from .device import Device
import time

# declare climate chamber over TCP, Port 57732
# clima = TCPLink('lan','129.217.167.99', 57732)


class LU114(Device):
    dv = None
    T_set = None
    Power = None

    def __init__(self, connection_type, host, port):
            super(LU114, self).__init__(connection_type=connection_type, host=host, port=port)

# Turn Device on or Off an set Temperature to 20°C
    def enablePower(self, bEnable):
        if bEnable:
            msg = self.ask('POWER, ON')
            print(msg)
            self.getAndSetParameter()
            self.Power = True
        elif not bEnable:
            self.setTemperature(20)
            msg = self.ask('MODE, STANDBY')
            print(msg)
            self.Power = False

    def getPowerStatus(self):
        msg = self.ask('MODE?')
        if msg == 'STANDBY':
            return False
        elif msg == 'CONSTANT'
            return True
        else:
            return "Mode uncertain, please check."
        pass

    def initialize(self):
        self.getAndSetParameter()
        pass

    def getAndSetParameter(self):
        #self.write('MODE, CONSTANT')
        #time.sleep(0.5)
        self.write('TEMP, S20')
        #self.Power = True
        return self.read()

    # def getAndSetParameter(self):
    #     self.Power = self.getPowerStatus()
    #     self.T_set = self.getSetTemperature()
    #     pass

    def setTemperature(self, Temp):
        if self.Power:
            msg = self.ask('TEMP, S%s' % Temp)
            self.T_set = Temp
            print(msg)
        else:
            self.enablePower(True)
            self.setTemperature(Temp)

    def getTemperature(self):
        msg = self.ask('TEMP?').split(',')
        return float(msg[0])

    def getSetTemperature(self):
        msg = self.ask('TEMP?').split(',')
        return float(msg[1])
    
    def userCmd(self, cmd):
        print("userCmd: %s" % cmd)
        return self.ask(cmd)

    def close(self):
        #self.close()
        pass

    def interaction(self):
        print('1: enable Power')
        print('2: set new Temperature')
        x = input('Number? \n')
        while x != '1' and x != '2':
            x = input('Possible Inputs: 1 or 2! \n')
        if x == '1':
            bO = input('Please enter ON or OFF! \n')
            if bO == 'ON' or bO == 'on':
                self.enablePower(1)
            elif bO == 'OFF' or bO == 'off':
                self.enablePower(0)
            else:
                pass
        if x == '2':
            fT = input('Please enter new Temperature in °C \n')
            self.setTemperature(float(fT))

    def output(self, show = True):
        bPower = self.Power
        if show:
            print('Climate Chamber:')
            if bPower:
                print('Power: \033[32m ON \033[0m')
            else:
                print('Power: \033[31m OFF \033[0m')
        else:
            fTset = -99.99
            fTac = -99.99
        fTset = self.getSetTemperature()
        fTac = self.getTemperature()
        if show:
            print('Temperature:' + '\t' + 'set: %.1f °C' % fTset + '\t' + 'actual: %.1f °C' % fTac)
        return([['Power', 'Tset[C]', 'Tac[C]'], [str(bPower), str(fTset), str(fTac)]])

