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
            msg = self.ask('MODE, CONSTANT')
            print(msg)
            self.Power = True
            self.setTemperature(20)
        else:
            msg = self.ask('MODE, STANDBY')
            print(msg)
            self.setTemperature(20)
            self.Power = False

    def getPowerStatus(self):
        msg = self.ask('MODE, DETAIL?')
        if msg == 'STANDY':
            return False
        else:
            return True
        pass

        def initialize(self):
            self.getAndSetParameter()
            pass

    def getAndSetParameter(self):
        self.write('MODE, CONSTANT')
        time.sleep(0.5)
        self.write('TEMP, S20')
        return self.dv.read()

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
        Tset = float(msg[1])
        return Tset
    
    def userCmd(self, cmd):
        print("userCmd: %s" % cmd)
        return self.ask(cmd)

    def close(self):
        self.close()
        pass
