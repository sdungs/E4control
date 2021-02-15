# -*- coding: utf-8 -*-

import math

from .device import Device


class K196(Device):
    mode = None

    def __init__(self, connection_type, host, port):
        super(K196, self).__init__(connection_type=connection_type, host=host, port=port)

    def userCmd(self, cmd):
        print('user cmd: %s' % cmd)
        return self.ask(cmd)

    def initialize(self, sMode):
        if (sMode == 'H'):
            self.setKind('DCV')
            self.setRange('RO')
            self.mode = 'H'
        elif (sMode in ['T',
                        'T2W']):  # the device itself selects 2- or 4-wire mode automatically (ohm sense leads connected or not)
            self.setKind('OHM')
            self.setRange('R2')
            self.mode = 'T'
        elif (sMode == 'V'):
            self.setKind('DCV')
            self.setRange('R0')
            self.mode = 'V'
        elif (sMode == 'I'):
            self.setKind('DCI')
            self.setRange('R0')
            self.mode = 'I'
        else:
            print('Initializing not possible: Unknown mode!')

    def setKind(self, sKind):
        if (sKind == 'DCV'):
            self.write('F0X')
        elif (sKind == 'ACV'):
            self.write('F1X')
        elif (sKind == 'OHM'):
            self.write('F2X')
        elif (sKind == 'DCI'):
            self.write('F3X')
        elif (sKind == 'ACI'):
            self.write('F4X')
        elif (sKind == 'dBV'):
            self.write('F5X')
        elif (sKind == 'dbI'):
            self.write('F6X')
        else:
            print('Unknown kind!')

    def setRange(self, sRange):
        if (sRange == 'R0'):
            self.write('R0X')
        elif (sRange == 'R1'):
            self.write('R1X')
        elif (sRange == 'R2'):
            self.write('R2X')
        elif (sRange == 'R3'):
            self.write('R3X')
        elif (sRange == 'R4'):
            self.write('R4X')
        elif (sRange == 'R5'):
            self.write('R5X')
        elif (sRange == 'R6'):
            self.write('R6X')
        elif (sRange == 'R7'):
            self.write('R7X')
        else:
            print('Unknown range!')

    def getStatus(self):
        return self.ask('U0X')

    def getKind(self):
        s = self.read()
        return s[0:4]

    def getValue(self, iChannel=-1):
        sValue = self.read()
        return float(sValue[4:16])

    def getResistance(self, iChannel=-1):
        fR = self.ask('N%iX' % iChannel)
        # self.write('N%iX' % iChannel)
        # fR = self.getValue()
        return float(fR[4:])

    def getTempPT100(self, iChannel=-1):
        a = 3.90802E-3
        b = -5.802E-7
        R0 = 100.00
        R = self.getValue()
        if R > 10000000:
            return (9999)
        return (-a / (2 * b) - math.sqrt(R / (R0 * b) - 1 / b + (a / (2 * b)) * (a / (2 * b))))

    def getTempPT1000(self, iChannel=-1):
        a = 3.90802E-3
        b = -5.802E-7
        R0 = 1000.00
        R = self.getValue()
        if R > 10000000:
            return (9999)
        return (-a / (2 * b) - math.sqrt(R / (R0 * b) - 1 / b + (a / (2 * b)) * (a / (2 * b))))

    def getHumidity(self, fTemp, iChannel=-1):
        a = 0.0315
        b = 0.826
        V = self.getValue()
        return ((V - b) / a) / (1.0546 - 0.00216 * fTemp)

    def getVoltage(self, iChannel=-1):
        fV = self.getValue()
        return (fV)

    def getCurrent(self, iChannel=-1):
        fV = self.getValue()
        return (fV)

    def setRange(self, sRange):
        if (sRange == 'R0'):
            self.write('R0X')
        elif (sRange == 'R1'):
            self.write('R1X')
        elif (sRange == 'R2'):
            self.write('R2X')
        elif (sRange == 'R3'):
            self.write('R3X')
        elif (sRange == 'R4'):
            self.write('R4X')
        elif (sRange == 'R5'):
            self.write('R5X')
        elif (sRange == 'R6'):
            self.write('R6X')
        elif (sRange == 'R7'):
            self.write('R7X')

    def writeOnDisplay(self, sMsg):
        msg = 'D' + sMsg + 'X'
        if (len(sMsg) <= 10):
            self.write(msg)
        else:
            print('Message to long!')

    def restart(self):
        self.write('L0X')

    def output(self, show=True):
        if show:
            print('K196:')
        values = []
        header = []
        if (self.mode == 'H'):
            fHumidity = self.getVoltage()
            if show:
                print('Humidity = %0.4f V' % fHumidity)
            values.append(str(fHumidity))
            header.append('H[V]')
        elif (self.mode == 'T'):
            fResistance = self.getResistance()
            fTemperature = self.getTempPT1000()
            values.append(str(fResistance))
            header.append('R[Ohm]')
            values.append(str(fTemperature))
            header.append('T[C]')
            if show:
                print('values:' + '\t' + '%.2f Ohm' % fResistance + '\t' + '%.1f °C' % fTemperature)
        elif (self.mode == 'V'):
            fVoltage = self.getVoltage()
            values.append(str(fVoltage))
            header.append('U[V]')
            if show:
                print('Voltage = %0.4f V' % fVoltage)
        else:
            print('Error!')
        return ([header, values])

    def interaction(self, gui=False):
        if gui:
            device_dict = {
                'pass': True,
            }
            return device_dict
        else:
            print('Nothing to do...')
