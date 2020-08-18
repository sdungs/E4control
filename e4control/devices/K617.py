# -*- coding: utf-8 -*-

import warnings

from .device import Device


class K617(Device):
    mode = None

    def __init__(self, connection_type, host, port):
        super(K617, self).__init__(connection_type=connection_type, host=host, port=port)

    def initialize(self, sMode):
        if (sMode == 'V'):
            self.setMeasurementMode('V')
            self.setRange('RO')
            self.performZeroCorrection()
        elif (sMode == 'I'):
            self.setMeasurementMode('I')
            self.setRange('R0')
            self.performZeroCorrection()
        elif (sMode == 'R'):
            self.setMeasurementMode('R')
            self.setRange('R0')
            self.performZeroCorrection()
        else:
            print('Initializing not possible: Unknown measurement mode!')

    def setMeasurementMode(self, sMode):
        if sMode in ('V', 'volts'):
            self.write('F0X')
            self.mode = 'V'
        elif sMode in ('I', 'amps', 'ampere', 'A'):
            self.write('F1X')
            self.mode = 'I'
        elif sMode in ('R', 'ohms'):
            self.write('F2X')
            self.mode = 'R'
        elif sMode in ('C', 'coulombs'):
            self.write('F3X')
        elif (sMode == 'external feedback'):
            self.write('F4X')
        elif (sMode == 'V/I ohms'):
            self.write('F5X')

    def getMeasurementMode(self):
        if self.mode is None:
            warnings.warn('The measurement mode not properly initialized. Please do this now via setMeasurementMode()')
        return self.mode

    def setRange(self, sRange):
        if sRange in ('R0', 'auto'):
            self.write('R0X')
            print('Changing to auto range.')
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
        elif (sRange == 'R8'):
            self.write('R8X')
        elif (sRange == 'R9'):
            self.write('R9X')
        elif (sRange == 'R10'):
            self.write('R10X')
        elif (sRange == 'R11'):
            self.write('R11X')
        elif sRange in ('R12', 'cancel'):
            self.write('R12X')

    def performZeroCorrection(self):
        self.write('Z0X')
        self.write('C1X')
        self.write('Z1X')
        self.write('C0X')
        print('Performed zero correction.')

    def getStatus(self, iChannel=-1):
        return self.ask('U0X')

    def getData(self, iChannel=-1):
        return self.read()

    def getValue(self, iChannel=-1):
        sValue = self.read()
        return float(sValue[4:])

    def getVoltage(self, iChannel=-1):
        if not (self.mode == 'V'):
            warnings.warn('Voltage mode not properly initialized. I\'m doing this for you now.')
            self.initialize('V')
        return self.getValue()

    def getCurrent(self, iChannel=-1):
        if not (self.mode == 'I'):
            warnings.warn('Current mode not properly initialized. I\'m doing this for you now.')
            self.initialize('I')
        return self.getValue()

    def getResistance(self, iChannel=-1):
        if not (self.mode == 'R'):
            warnings.warn('Resistance mode not properly initialized. I\'m doing this for you now.')
            self.initialize('R')
        return self.getValue()

    def output(self, sMode=mode, show=True):
        if show:
            print('K617:')
            print('Not yet implemeted...')
        values = []
        header = []
        # if (sMode == 'H'):
        #     fHumidity = self.getVoltage()
        #     if show:
        #         print('Humidity = %0.4f V' % fHumidity)
        #     values.append(str(fHumidity))
        #     header.append('H[V]')
        # elif (sMode == 'T'):
        #     fResistance = self.getResistance()
        #     fTemperature = self.getTempPT1000()
        #     values.append(str(fResistance))
        #     header.append('R[Ohm]')
        #     values.append(str(fTemperature))
        #     header.append('T[C]')
        #     if show:
        #         print('values:'+'\t'+'%.2f Ohm' % fResistance + '\t' + '%.1f °C' % fTemperature)
        # elif (sMode == 'V'):
        #     fVoltage = self.getVoltage()
        #     values.append(str(fVoltage))
        #     header.append('U[V]')
        #     if show:
        #         print('Voltage = %0.4f V' % fVoltage)
        # else:
        #     print('Error!')
        return([header, values])

    def interaction(self):
        print('Not yet implemeted...')
