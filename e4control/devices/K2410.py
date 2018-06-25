# -*- coding: utf-8 -*-

from time import sleep

from .device import Device


class K2410(Device):
    rampSpeed_step = 10
    rampSpeed_delay = 1  # s

    def __init__(self, connection_type, host, port):
        super(K2410, self).__init__(
            connection_type=connection_type, host=host, port=port)

    def userCmd(self, cmd):
        print('user cmd: %s' % cmd)
        return self.ask(cmd)

    def initialize(self, iChannel=-1):
        self.setCurrentAutoRange(True)
        self.setVoltageRange('MAX')
        pass

    def setCurrentAutoRange(self, bsetCurrentAutoRange):
        if bsetCurrentAutoRange:
            self.write(':SOUR:CURR:RANG:AUTO ON')
        else:
            self.write(':SOUR:CURR:RANG:AUTO OFF')

    def setVoltageAutoRange(self, bsetVoltageAutoRange):
        if bsetVoltageAutoRange:
            self.write(':SOUR:VOLT:RANG:AUTO ON')
        else:
            self.write(':SOUR:VOLT:RANG:AUTO OFF')

    def setVoltageRange(self, sRange):
        if sRange == 'MAX':
            self.write(':SOUR:VOLT:RANG MAX')
        elif sRange == 'MIN':
            self.write(':SOUR:VOLT:RANG MIN')
        elif sRange == 'AUTO':
            self.write(':SOUR:VOLT:RANG:AUTO ON')
        else:
            print('Unknown Range')

    def setCurrentLimit(self, fIlim, iChannel=-1):
        self.write(':SENSE:CURR:PROT %f' % fIlim)

    def setVoltageLimit(self, fVlim, iChannel=-1):
        self.write(':SENSE:VOLT:PROT %f' % fVlim)

    def setCurrent(self, fIset, iChannel=-1):
        self.write(':SOUR:CURR %f' % fIset)

    def setVoltage(self, fVset, iChannel=-1):
        self.write(':SOUR:VOLT %f' % fVset)

    def enableOutput(self, bEnable, iChannel=-1):
        if bEnable:
            self.write(':OUTPUT ON')
        else:
            self.write(':OUTPUT OFF')

    def getEnableOutput(self, iChannel=-1):
        return self.ask(':OUTPUT?')

    def getVoltage(self, iChannel=-1):
        sValues = self.ask(':READ?')
        if ',' not in sValues:
            return -999.
        return float(sValues.split(',')[0])

    def getCurrent(self, iChannel=-1):
        sValues = self.ask(':READ?')
        return float(sValues.split(',')[1])

    def getCurrentLimit(self, iChannel=-1):
        sCurrLim = self.ask(':SENSE:CURR:PROT?')
        return float(sCurrLim)

    def getVoltageLimit(self, iChannel=-1):
        sVoltLim = self.ask(':SENSE:VOLT:PROT?')
        return float(sVoltLim)

    def setRampSpeed(self, iRampSpeed, iDelay):
        if iRampSpeed < 1 or iRampSpeed > 255:
            print('Set RampSpeed size is out off range!')
        else:
            self.rampSpeed_step = iRampSpeed
        if iDelay < 0:
            print('No negativ Delay is possible!')
        else:
            self.rampSpeed_delay = iDelay

    def getRampSpeed(self):
        return([int(self.rampSpeed_step), int(self.rampSpeed_delay)])

    def rampVoltage(self, fVnew, iChannel=-1):
        V = self.getVoltage(iChannel)
        V = round(V, 4)
        if abs(fVnew - V) <= self.rampSpeed_step:
            self.setVoltage(fVnew, iChannel)
            print('Voltage reached: %.2f V' % fVnew)
        else:
            self.setVoltage(V + self.rampSpeed_step *
                            (fVnew - V) / abs(fVnew - V))
            print('Ramp Voltage: %.2f V' %
                  (V + self.rampSpeed_step * (fVnew - V) / abs(fVnew - V)))
            sleep(self.rampSpeed_delay)
            self.rampVoltage(fVnew, iChannel)
            pass

    def setOutputSide(self, sside):
        if (sside == 'front'):
            self.write(':ROUT:TERM FRON')
        elif (sside == 'back'):
            self.write(':ROUT:TERM REAR')

    def getOutputSide(self):
        return(self.ask(':ROUT:TERM?'))

    def reset(self):
        self.write('*RST')

    def output(self, show=True):
        bPower = self.getEnableOutput()
        fLimit = self.getCurrentLimit() * 1E6
        if show:
            print('K2410:')
            if bPower == '1':
                print('Output \033[32m ON \033[0m')
            else:
                print('Output \033[31m OFF \033[0m')
            print('Current Limit: %0.1f uA' % fLimit)
        if bPower == '1':
            fVoltage = self.getVoltage()
            fCurrent = self.getCurrent() * 1E6
            if show:
                print('Voltage = %0.1f V' % fVoltage)
                print('Current = %0.3f uA' % fCurrent)
        else:
            if show:
                print('Voltage = ---- V')
                print('Current = ---- uA')
            fVoltage = 0
            fCurrent = 0
        return([['Output', 'Ilim[uA]', 'U[V]', 'I[uA]'], [str(bPower), str(fLimit), str(fVoltage), str(fCurrent)]])

    def interaction(self):
        print('1: enable Output')
        print('2: set Voltage')
        x = raw_input('Number? \n')
        while x != '1' and x != '2':
            x = raw_input('Possible Inputs: 1 or 2! \n')
        if x == '1':
            bO = raw_input('Please enter ON or OFF! \n')
            if bO == 'ON' or bO == 'on':
                self.enableOutput(True)
            else:
                self.rampVoltage(0)
                self.enableOutput(False)
        elif x == '2':
            fV = raw_input('Please enter new Voltage in V \n')
            self.rampVoltage(float(fV))
