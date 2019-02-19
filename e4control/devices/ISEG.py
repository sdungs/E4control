# -*- coding: utf-8 -*-

from time import sleep

from .device import Device


class ISEG(Device):
    rampSpeed_step = 5
    rampSpeed_delay = 1  # s

    def __init__(self, connection_type, host, port):
        super(ISEG, self).__init__(connection_type=connection_type, host=host, port=port)
        self.setHardwareRampSpeed(255, 1)
        self.setHardwareRampSpeed(255, 2)

    def userCmd(self, cmd):
        print('user cmd: %s' % cmd)
        return self.ask(cmd)

    def initialize(self, iChannel=-1):
        pass

    def enableOutput(self, bEnable, iChannel=-1):
        pass

    def getVoltage(self, iChannel):
        sV = self.ask('U%i' % iChannel)
        sV = sV.replace('U%i' % iChannel, '')
        fV = float(sV[:-3]) * 10**float(sV[-3:])
        return fV

    def getCurrent(self, iChannel):
        sI = self.ask('I%i' % iChannel)
        sI = sI.replace('I%i' % iChannel, '')
        fI = float(sI[:-3]) * 10**float(sI[-3:])
        return fI

    def setCurrentLimit(self, iChannel):
        # just manual setting possible
        pass

    def setVoltageLimit(self, iChannel):
        # just manual setting possible
        pass

    def getVoltageLimit(self, iChannel):
        sVoltLim = self.ask('M%i' % iChannel)
        sVoltLim = sVoltLim.replace('M%i' % iChannel, '')
        return float(sVoltLim)

    def getCurrentLimit(self, iChannel):
        sCurrentLim = self.ask('N%i' % iChannel)
        sCurrentLim = sCurrentLim.replace('N%i' % iChannel, '')
        return (float(sCurrentLim) * 6 * 1E3 / 100)

    def getSetVoltage(self, iChannel):
        sV = self.ask('D%i' % iChannel)
        sV = sV.replace('D%i' % iChannel, '')
        fV = float(sV[:-3]) * 10**float(sV[-3:])
        return fV

    def getHardwareRampSpeed(self, iChannel):
        sRamp = self.ask('V%i' % iChannel)
        sRamp = sRamp.replace('V%i' % iChannel, '')
        return int(sRamp)

    def setVoltage(self, fValue, iChannel):
        self.ask('D%i=%.1f' % (iChannel, abs(fValue)))
        self.startRampU(iChannel)

    def setHardwareRampSpeed(self, iRampSpeed, iChannel):
        if iRampSpeed < 1 or iRampSpeed > 255:
            print('Set RampSpeed is out of range!')
        else:
            self.ask('V%i=%i' % (iChannel, iRampSpeed))

    def setRampSpeed(self, iRampSpeed, iDelay):
        if iRampSpeed < 1 or iRampSpeed > 255:
            print('Set RampSpeed size is out of range!')
        else:
            self.rampSpeed_step = iRampSpeed
        if iDelay < 0:
            print('No negativ Delay is possible!')
        else:
            self.rampSpeed_delay = iDelay

    def getRampSpeed(self):
        return([int(self.rampSpeed_step), int(self.rampSpeed_delay)])

    def rampVoltage(self, fVnew, iChannel):
        fVnew = abs(fVnew)
        V = self.getVoltage(iChannel)
        V = round(V, 4)
        if abs(fVnew - abs(V)) <= self.rampSpeed_step:
            self.setVoltage(fVnew, iChannel)
            print('Voltage reached: %.2f V' % fVnew)
        else:
            self.setVoltage(abs(V) + self.rampSpeed_step * (fVnew - abs(V)) / abs(fVnew - abs(V)), iChannel)
            print('Ramp Voltage: %.2f V' % (abs(V) + self.rampSpeed_step * (fVnew - abs(V)) / abs(fVnew - abs(V))))
            sleep(self.rampSpeed_delay)
            self.rampVoltage(fVnew, iChannel)

    def getStatus(self, iChannel):
        s = self.ask('S%i' % iChannel)
        s = s.replace('S%i=' % iChannel, '')
        return s

    def startRampU(self, iChannel):
        sRamp = self.ask('G%i' % iChannel)
        sRamp = sRamp.replace('G%i' % iChannel, '')
        print(sRamp)

    def output(self, show=True):
        f1Limit = self.getCurrentLimit(1) * 1E6
        f2Limit = self.getCurrentLimit(2) * 1E6
        f1Voltage = self.getVoltage(1)
        f2Voltage = self.getVoltage(2)
        f1Current = self.getCurrent(1) * 1E6
        f2Current = self.getCurrent(2) * 1E6

        if show:
            print('ISEG:')
            print('CH 1:' + '\t' + 'I_lim = %.2fuA' % f1Limit)
            print('Voltage = %.1fV' % f1Voltage + '\t' + 'Current = %.3fuA' % f1Current)
            print('CH 2:' + '\t' + 'I_lim = %.2fuA' % f2Limit)
            print('Voltage = %.1fV' % f2Voltage + '\t' + 'Current = %.3fuA' % f2Current)
        return([['Ilim1[uA]', 'U1[V]', 'I1[uA]', 'Ilim2[uA]', 'U2[V]', 'I2[uA]'], [str(f1Limit), str(f1Voltage), str(f1Current), str(f2Limit), str(f2Voltage), str(f2Current)]])

    def interaction(self):
        sChannel = input('Choose channel! \n')
        while sChannel != '1' and sChannel != '2':
            sChannel = input('Possible Channels: 1 or 2! \n')
        iChannel = int(sChannel)
        print('1: set Voltage')
        x = input('Number? \n')
        while x != '1':
            x = input('Possible Inputs: 1! \n')
        if x == '1':
            fV = input('Please enter new Voltage in V for CH %i\n' % iChannel)
            self.rampVoltage(float(fV), iChannel)
