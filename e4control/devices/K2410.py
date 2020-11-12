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
        self.write(':SENS:FUNC "VOLT", "CURR"')
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

    def setOutput(self, bEnable, iChannel=-1):
        if bEnable:
            self.write(':OUTPUT ON')
        else:
            self.write(':OUTPUT OFF')

    def getOutput(self, iChannel=-1):
        return self.ask(':OUTPUT?')

    def getVoltage(self, iChannel=-1):
        sValues = self.ask(':READ?')
        if ',' not in sValues:
            sValues = self.ask(':READ?')
            if ',' not in sValues:
                return 'error'
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
            print('Set RampSpeed size is out of range!')
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
        bPower = self.getOutput()
        fLimit = self.getCurrentLimit() * 1E6

        if bPower == '1':
            fVoltage = self.getVoltage()
            fCurrent = self.getCurrent() * 1E6
        else:
            fVoltage = 0
            fCurrent = 0

        if show:
            self.printOutput('K2410:')
            if bPower == '1':
                self.printOutput('Output \033[32m ON \033[0m')
                self.printOutput('Current Limit: %0.1f uA' % fLimit)
                self.printOutput('Voltage = %0.1f V' % fVoltage)
                self.printOutput('Current = %0.3f uA' % fCurrent)
            else:
                self.printOutput('Output \033[31m OFF \033[0m')
                self.printOutput('Current Limit: %0.1f uA' % fLimit)
                self.printOutput('Voltage = ---- V')
                self.printOutput('Current = ---- uA')

        return([['Output', 'Ilim[uA]', 'U[V]', 'I[uA]'], [str(bPower), str(fLimit), str(fVoltage), str(fCurrent)]])

    def interaction(self, gui=False):
        if gui:
            device_dict = {
			'toogleOutput': True,
			'rampVoltage': True,
			'setCurrentLimit': True,
			}
            return device_dict
        else:
            print(
                '0: Continue dcs mode without any changes\n'
                '1: Toggle output\n'
                '2: Set voltage (enables the output if its off)\n'
                '3: Set currrent limit'
                )

            x = input('Number? \n')
            while not (x in ['0','1','2','3',]):
                x = input('Possible Inputs: 0, 1, 2 or 3! \n')

            if x == '0':
                pass
            elif x == '1':
                if self.getOutput() == '1':
                    self.rampVoltage(0)
                    self.setOutput(False)
                else:
                    self.setOutput(True)
            elif x == '2':
                fV = input('Please enter new Voltage in V \n')
                if not self.getOutput() == '1':
                    print('Enabled output. Now ramping...')
                    self.setOutput(True)
                self.rampVoltage(float(fV))
            elif x == '3':
                fIlim = input('Please enter new current limit in uA \n')
                self.setCurrentLimit(float(fIlim)/1E6)
