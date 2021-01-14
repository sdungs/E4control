# -*- coding: utf-8 -*-

import math

from .device import Device


class K2000(Device):
    mode = None

    def __init__(self, connection_type, host, port):
        super(K2000, self).__init__(connection_type=connection_type, host=host, port=port)

    def userCmd(self, cmd):
        print('user cmd: %s' % cmd)
        return self.ask(cmd)

    def initialize(self, sMode):
        # self.write(':SYTS:BEEP:STAT OFF')
        if (sMode == 'H'):
            self.setKind('DCV')
            self.setRange('RO')
            self.mode = 'H'
        elif (sMode == 'T2W'):
            self.setKind('OHM') # 2-wire measurment
            self.setRange('R2')
            self.mode = 'T2W'
        elif (sMode == 'T'):
            self.setKind('OHM4') # 4-wire measurment
            self.setRange('R2')
            self.mode = 'T'
        elif (sMode == 'V'):
            self.setKind('DCV')
            self.setRange('R4')
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
        elif (sKind == 'OHM4'):
            self.write('F9X')
        elif (sKind == 'DCI'):
            self.write('F3X')
        elif (sKind == 'ACI'):
            self.write('F4X')
        elif (sKind == 'dBV'):
            self.write('F5X')
        elif (sKind == 'F'):
            self.write('F7X')
        elif (sKind == 'T'):
            self.write('F8X')
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

    def getStatus(self, iChannel=-1):
        return self.ask('U0X')

    def getKind(self):
        # self.ask('U0X')
        sKind = self.read()
        # return s[0:4]
        return(sKind)

    def getValue(self):
        # self.ask('U0X')
        sValue = self.read()
        return float(sValue[4:])

    def getResistance(self, iChannel):
        fR = self.ask('N%iX' % iChannel)
        # self.write('N%iX' % iChannel)
        # fR = self.getValue()
        return float(fR[4:])

    def getVoltage(self, iChannel):
        self.write('N%iX' % iChannel)
        fV = self.getValue()
        return fV

    def getTemperature(self, iChannel):
        return self.getTempPT1000(iChannel)

    def getTempPT100(self, iChannel):
        a = 3.90802E-3
        b = -5.802E-7
        R0 = 100.00
        R = self.getResistance(iChannel)
        return (-a/(2*b)-math.sqrt(R/(R0*b)-1/b+(a/(2*b))*(a/(2*b))))

    def getTempPT1000(self, iChannel):
        a = 3.90802E-3
        b = -5.802E-7
        R0 = 1000.00
        R = self.getResistance(iChannel)
        if R > 10000000:
            return(9999)
        return (-a/(2*b)-math.sqrt(R/(R0*b)-1/b+(a/(2*b))*(a/(2*b))))

    def getTempPT1000all(self):
        a = 3.90802E-3
        b = -5.802E-7
        R0 = 1000.00
        Ts = []
        i = 1
        while i <= 5:
            R = self.getResistance(i)
            if R > 10000000:
                Ts.append(9999)
            else:
                Ts.append(-a/(2*b)-math.sqrt(R/(R0*b)-1/b+(a/(2*b))*(a/(2*b))))
            i += 1
        return(Ts)

    def getHumidity(self, fTemp, iChannel):
        a = 0.0315
        b = 0.826
        V = self.getVoltage(iChannel)
        return ((V-b)/a)/(1.0546-0.00216*fTemp)

    def restart(self):
        self.write('L0X')

    def output(self, show=True):
        if show:
            self.printOutput('K2000:')
        values = []
        header = []
        if (self.mode == 'H'):
            fHumidity = self.getVoltage(1)
            if show:
                self.printOutput('Humidity = %0.4f V' % fHumidity)
            values.append(str(fHumidity))
            header.append('H[V]')
        elif (self.mode == 'T2W'):
            i = 1
            while i <= 10:
                fResistance = self.getResistance(i)
                fTemperature = self.getTempPT1000(i)
                values.append(str(fResistance))
                header.append('R%i[Ohm]' % i)
                values.append(str(fTemperature))
                header.append('T%i[C]' % i)
                if show:
                    self.printOutput('Ch %i:' % i+'\t'+'%.2f Ohm' % fResistance + '\t' + '%.1f C' % fTemperature)
                i += 1
        elif (self.mode == 'T'):
            i = 1
            while i <= 5:
                fResistance = self.getResistance(i)
                fTemperature = self.getTempPT1000(i)
                values.append(str(fResistance))
                header.append('R%i[Ohm]' % i)
                values.append(str(fTemperature))
                header.append('T%i[C]' % i)
                if show:
                    self.printOutput('Ch %i:' % i+'\t'+'%.2f Ohm' % fResistance + '\t' + '%.1f °C' % fTemperature)
                i += 1
        elif (self.mode == 'V'):
            fVoltage = self.getVoltage(1)
            if show:
                self.printOutput('Voltage = %0.4f V' % fVoltage)
            values.append(str(fVoltage))
            header.append('U[V]')
        else:
            self.printOutput('Error!')
        return([header, values])

    def interaction(self, gui=False):
        if gui:
            device_dict = {
            'pass': True,
            }
            return device_dict
        else:
            print('Nothing to do...')
