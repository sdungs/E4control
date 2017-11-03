# -*- coding: utf-8 -*-

from .device import Device


class SB22(Device):
    T_set = None
    H_set = None
    Power = None
    D_2 = None
    D_3 = None
    D_4 = None
    D_5 = None
    D_6 = None
    D_7 = None
    D_8 = '0'
    D_9 = '0'
    D_10 = '0'
    D_11 = '0'
    D_12 = '0'
    D_13 = '0'
    D_14 = '0'
    D_15 = '0'
    D_16 = '0'

    def __init__(self, connection_type, host, port):
        super(SB22, self).__init__(connection_type=connection_type, host=host, port=port)
        self.getAndSetParameter()

    def userCmd(self, cmd):
        print('user cmd: %s' % cmd)
        return self.ask(cmd)

    def initialize(self, iChannel=-1):
        self.getAndSetParameter()

    def generateChecksum(self, cmd):
        B = 0
        for i in cmd:
            J = ord(i)
            B = B - J
            if (B < -255):
                B = B + 256
        B = 256 + B
        J = B/16
        if (J < 10):
            J = J + 48
        else:
            J = J + 55
        K = B % 16
        if (K < 10):
            K = K + 48
        else:
            K = K + 55
        result = chr(J) + chr(K)
        return result

    def updateChanges(self):
        line = chr(02)+'1T%sF%sR%s%s%s%s%s%s%s000000000' % (self.T_set, self.H_set, self.Power, self.D_2, self.D_3, self.D_4, self.D_5, self.D_6, self.D_7)
        pn = self.generateChecksum(line)
        cmd = '%s%s' % (line, pn)+chr(03)
        self.write(cmd)

    def enablePower(self, bEnable):
        if bEnable:
            self.Power = '1'
        else:
            self.Power = '0'
        self.updateChanges()

    def getStatus(self):
        return self.ask(chr(02)+'1?8E\3'+chr(03))

    def getAndSetParameter(self):
        s = self.getStatus()
        if (s.find('#') >= 0):
            p = s.split('#')[1]
        else:
            p = s.split('$')[1]
        line = p[p.find('R')+1:p.find('R')+8]
        self.Power = line[0]
        self.D_2 = line[1]
        self.D_3 = line[2]
        self.D_4 = line[3]
        self.D_5 = line[4]
        self.D_6 = line[5]
        self.D_7 = line[6]
        self.T_set = p[p.find('T')+1:p.find('F')]
        self.H_set = p[p.find('F')+1:p.find('R')]

    def setTemperature(self, fValue):
        self.T_set = '%.1f' % fValue
        self.updateChanges()

    def getSetTemperature(self):
        return float(self.T_set)

    def getTemperature(self, iChannel=-1):
        s = self.getStatus()
        if (s.find('#') >= 0):
            p = s.split('#')[0]
        else:
            p = s.split('$')[0]
        v = p[p.find('T')+1:p.find('F')]
        v = v.replace('&', '.')
        return float(v)

    def setHumidity(self, fValue):
        self.H_set = '%.1f' % fValue
        self.updateChanges()

    def getSetHumidity(self, iChannel=-1):
        return int(self.H_set)

    def getHumidity(self):
        s = self.getStatus()
        if (s.find('#') >= 0):
            p = s.split('#')[0]
        else:
            p = s.split('$')[0]
        v = p[p.find('F')+1:p.find('P')]
        return int(v)

    def getError(self):
        sStatus = self.getStatus()
        if (sStatus.find('#') >= 0):
            sError = sStatus[sStatus.find('#')+1:sStatus.find('T')]
        else:
            sError = sStatus[sStatus.find('$')+1:sStatus.find('T')]
        return sError

    def setOperationMode(self, sMode):
        if (sMode == 'climate'):
            self.D_2 = '0'
        elif (sMode == 'normal'):
            self.D_2 = '1'
        else:
            print('Unknown mode: %s' % sMode)
        self.updateChanges()

    def getOperationMode(self):
        if (self.D_2 == '0'):
            sMode = 'climate'
        else:
            sMode = 'normal'
        return sMode

    def enableProtectionSystem(self, bEnable):
        if bEnable:
            self.D_3 = '1'
        else:
            self.D_3 = '0'

    def enableDewPointExtension(self, bEnable):
        if bEnable:
            self.D_4 = '1'
        else:
            self.D_4 = '0'

    def enableCapacitiveHumidity(self, bEnable):
        if bEnable:
            self.D_5 = '1'
        else:
            self.D_5 = '0'

    def enableEngerySavingMode(self, bEnable):
        if bEnable:
            self.D_6 = '1'
        else:
            self.D_6 = '0'

    def enableAdjustableAirFanSpeed(self, bEnable):
        if bEnable:
            self.D_7 = '1'
        else:
            self.D_7 = '0'

    def output(self,  show=True):
        sMode = self.getOperationMode()
        bPower = self.Power
        if show:
            print('Climate Chamber:')
            print('Mode: ' + sMode)
            if bPower == '1':
                print('Power: \033[32m ON \033[0m')
            else:
                print('Power: \033[31m OFF \033[0m')
        if (self.D_2 == '0'):
            fHset = self.getSetHumidity()
            fHac = self.getHumidity()
            if show:
                print('Humidity:' + '\t' + 'set: %.1f' % fHset + '\t' + 'actual: %.1f' % fHac)
        else:
            fHset = -1
            fHac = -1
        fTset = self.getSetTemperature()
        fTac = self.getTemperature()
        if show:
            print('Temperature:' + '\t' + 'set: %.1f °C' % fTset + '\t' + 'actual: %.1f °C' % fTac)
        return([['Mode', 'Power', 'Hset', 'Hac', 'Tset[C]', 'Tac[C]'], [str(sMode), str(bPower), str(fHset), str(fHac), str(fTset), str(fTac)]])

    def interaction(self):
        print('1: enable Power')
        print('2: change Mode')
        print('3: set new Temperature')
        print('4: set new Humidity')
        x = raw_input('Number? \n')
        while x != '1' and x != '2' and x != '3' and x != '4':
            x = raw_input('Possible Inputs: 1,2,3 or 4! \n')
        if x == '1':
            bO = raw_input('Please enter ON or OFF! \n')
            if bO == 'ON' or bO == 'on':
                self.enablePower(1)
            elif bO == 'OFF' or bO == 'off':
                self.enablePower(0)
            else:
                pass
        elif x == '2':
            sM = raw_input('choose: climate or normal \n')
            self.setOperationMode(sM)
        elif x == '3':
            fT = raw_input('Please enter new Temperature in °C \n')
            self.setTemperature(float(fT))
        elif x == '4':
            if (self.D_2 == '0'):
                fH = raw_input('Please enter new Humidity \n')
                self.setHumidity(float(fH))
            else:
                print('Please change mode to climate before!')
