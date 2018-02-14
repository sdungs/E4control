# -*- coding: utf-8 -*-
from .device import Device
import time

# declare climate chamber over TCP, Port 57732
# clima = TCPLink('lan','129.217.167.99', 57732)


class LU114:
    dv = None
    T_set = None
    Power = None

    def __init__(self, connection_type, host, port):
            super(LU114, self).__init__(connection_type=connection_type, host=host, port=port)

# Turn Device on or Off an set Temperature to 20°C
    def enablePower(self, bEnable):
        if bEnable:
            msg = self.dv.ask('POWER, ON')
            print(msg)
            msg = self.dv.ask('MODE, CONSTANT')
            print(msg)
            self.Power = True
            self.setTemperature(20)
        else:
            msg = self.dv.ask('MODE, STANDBY')
            print(msg)
            self.setTemperature(20)
            self.Power = False

    def getPowerStatus(self):
        msg = self.dv.ask('MODE, DETAIL?')
        if msg == 'STANDY':
            return False
        else:
            return True
        pass

        def initialize(self):
            self.getAndSetParameter()
            pass

    def getAndSetParameter(self):
        self.dv.write('MODE, CONSTANT')
        time.sleep(0.5)
        self.dv.write('TEMP, S20')
        return self.dv.read()

    # def getAndSetParameter(self):
    #     self.Power = self.getPowerStatus()
    #     self.T_set = self.getSetTemperature()
    #     pass

    def setTemperature(self, Temp):
        if self.Power:
            msg = self.dv.ask('TEMP, S%s' % Temp)
            self.T_set = Temp
            print(msg)
        else:
            self.enablePower(True)
            self.setTemperature(Temp)

    def getTemperature(self):
        msg = self.dv.ask('TEMP?').split(',')
        return float(msg[0])

    def getSetTemperature(self):
        msg = self.dv.ask('TEMP?').split(',')
        Tset = float(msg[1])
        return Tset

    # Thermal cycling between Temp1 and Temp2, with waiting period (in minutes)
    # after reaching set Temp for defined number of cycles
    def ThermalCycling(self, Temp1, Temp2, t_wait, cycles):
        for i in range(0, cycles):
            self.setTemperature(Temp1)
            arrived = False
            while arrived == False:
    # print('Checked if ramping is finished')
                if self.RampingFinished(Temp1):
                    time.sleep(t_wait * 60)
                    arrived = True
                time.sleep(30)
            self.setTemperature(Temp2)
            arrived = False
            while arrived == False:
                if self.RampingFinished(Temp2):
                    time.sleep(t_wait * 60)
                    arrived = True

    def RampingFinished(self, Temp):
        T_is = self.getTemperature()
        if abs(T_is - Temp) <= 0.2:
            return True
        else:
            print('Remaining temperature difference: ' + str(abs(T_is - Temp)))
            return False

    def userCmd(self, cmd):
        print("userCmd: %s" % cmd)
        return self.dv.ask(cmd)

    def close(self):
        self.dv.close()
        pass
