# -*- coding: utf-8 -*-

import time

from .device import Device


class JULABO(Device):
    T_set = None
    Power = None
    Mode = None

    def __init__(self, connection_type, host, port):
        super(JULABO, self).__init__(connection_type=connection_type, host=host, port=port)
        self.getAndSetParameter()

    def userCmd(self, cmd):
        print('user cmd: %s' % cmd)
        return self.ask(cmd)

    def initialize(self, iChannel=-1):
        self.getAndSetParameter()

    def enablePower(self, bEnable, iChannel=-1):
        if bEnable:
            self.write('out_mode_05 1')
            self.Power = '1'
        else:
            self.write('out_mode_05 0')
            self.Power = '0'

    def getPowerStatus(self, iChannel=-1):
        return self.ask('in_mode_05')

    def getStatus(self, iChannel=-1):
        return self.ask('status')

    def getAndSetParameter(self):
        self.Power = self.getPowerStatus()
        self.T_set = self.getSetTemperature()
        self.Mode = self.getOperationMode()
        pass

    def setTemperature(self, fValue, iChannel=-1):
        self.write('out_sp_00 {:2.1f}'.format(fValue))
        pass

    def getSetTemperature(self, iChannel=-1):
        return float(self.ask('in_sp_00'))

    def getInTemperature(self, iChannel=-1):
        return float(self.ask('in_pv_00'))

    def getExTemperature(self, iChannel=-1):
        return float(self.ask('in_pv_02'))

    def getHeaterPower(self, iChannel=-1):
        return float(self.ask('in_pv_01'))

    def setOperationMode(self, sMode, iChannel=-1):
        if (sMode == 'int'):
            self.write('out_mode_04 0')
            self.Mode = 'int'
        elif (sMode == 'ext'):
            self.write('out_mode_04 1')
            self.Mode = 'ext'
        else:
            print('Unknown mode:{:s}'.format(sMode))

    def getOperationMode(self, iChannel=-1):
        if (self.ask('in_mode_04') == '0'):
            return('int')
        else:
            return('ext')

    def output(self,  show=True):
        sMode = self.Mode
        bPower = self.Power
        if show:
            print('Julabo:')
            print('Mode: ' + sMode)
            if bPower == '1':
                print('Power: \033[32m ON \033[0m')
            else:
                print('Power: \033[31m OFF \033[0m')
        fTset = self.getSetTemperature()
        fTin = self.getInTemperature()
        try:
            fTex = self.getExTemperature()
        except ValueError:
            fTex = 9999
        fHeat = self.getHeaterPower()
        if show:
            print('T_set = %.1f°C' % fTset + '\t' + 'Heater Power = %.1f ' % fHeat)
            print('T_in = %.1f°C' % fTin + '\t' + 'T_ex = %.1f°C' % fTex)

        return([['Mode', 'Power', 'Tset[C]', 'Tin[C]', 'Tex[C]', 'Pheat[]'], [str(sMode), str(bPower), str(fTset), str(fTin), str(fTex), str(fHeat)]])

    def interaction(self):
        print('1: enable Power')
        print('2: change Mode')
        print('3: set new Temperature')
        x = input('Number? \n')
        while x != '1' and x != '2' and x != '3':
            x = input('Possible Inputs: 1,2 or 3! \n')
        if x == '1':
            bO = input('Please enter ON or OFF! \n')
            if bO == 'ON' or bO == 'on':
                self.enablePower(1)
            elif bO == 'OFF' or bO == 'off':
                self.enablePower(0)
            else:
                pass
        elif x == '2':
            sM = input('choose: int or ext \n')
            self.setOperationMode(sM)
        elif x == '3':
            fT = input('Please enter new Temperature in °C \n')
            self.setTemperature(float(fT))
            time.sleep(0.5)
